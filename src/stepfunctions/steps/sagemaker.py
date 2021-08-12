# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License").
# You may not use this file except in compliance with the License.
# A copy of the License is located at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# or in the "license" file accompanying this file. This file is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied. See the License for the specific language governing
# permissions and limitations under the License.
from __future__ import absolute_import

import logging
import operator

from enum import Enum
from functools import reduce

from stepfunctions.exceptions import InvalidPathToPlaceholderParameter
from stepfunctions.inputs import Placeholder
from stepfunctions.steps.constants import placeholder_paths
from stepfunctions.steps.states import Task
from stepfunctions.steps.fields import Field
from stepfunctions.steps.utils import tags_dict_to_kv_list
from stepfunctions.steps.integration_resources import IntegrationPattern, get_service_integration_arn

from sagemaker.workflow.airflow import training_config, transform_config, model_config, tuning_config, processing_config
from sagemaker.model import Model, FrameworkModel
from sagemaker.model_monitor import DataCaptureConfig
from sagemaker.processing import ProcessingJob

logger = logging.getLogger('stepfunctions.sagemaker')

SAGEMAKER_SERVICE_NAME = "sagemaker"

class SageMakerApi(Enum):
    CreateTrainingJob = "createTrainingJob"
    CreateTransformJob = "createTransformJob"
    CreateModel = "createModel"
    CreateEndpointConfig = "createEndpointConfig"
    UpdateEndpoint = "updateEndpoint"
    CreateEndpoint = "createEndpoint"
    CreateHyperParameterTuningJob = "createHyperParameterTuningJob"
    CreateProcessingJob = "createProcessingJob"


class SageMakerTask(Task):

    """
    Task State causes the interpreter to execute the work identified by the state’s `resource` field.
    """

    def __init__(self, state_id, step_type, tags, **kwargs):
        """
        Args:
            state_id (str): State name whose length **must be** less than or equal to 128 unicode characters. State names **must be** unique within the scope of the whole state machine.
            resource (str): A URI that uniquely identifies the specific task to execute. The States language does not constrain the URI scheme nor any other part of the URI.
            timeout_seconds (int, optional): Positive integer specifying timeout for the state in seconds. If the state runs longer than the specified timeout, then the interpreter fails the state with a `States.Timeout` Error Name. (default: 60)
            timeout_seconds_path (str, optional): Path specifying the state's timeout value in seconds from the state input. When resolved, the path must select a field whose value is a positive integer.
            heartbeat_seconds (int, optional): Positive integer specifying heartbeat timeout for the state in seconds. This value should be lower than the one specified for `timeout_seconds`. If more time than the specified heartbeat elapses between heartbeats from the task, then the interpreter fails the state with a `States.Timeout` Error Name.
            heartbeat_seconds_path (str, optional): Path specifying the state's heartbeat value in seconds from the state input. When resolved, the path must select a field whose value is a positive integer.
            comment (str, optional): Human-readable comment or description. (default: None)
            input_path (str, optional): Path applied to the state’s raw input to select some or all of it; that selection is used by the state. (default: '$')
            parameters (dict, optional): The value of this field becomes the effective input for the state.
            result_path (str, optional): Path specifying the raw input’s combination with or replacement by the state’s result. (default: '$')
            output_path (str, optional): Path applied to the state’s output after the application of `result_path`, producing the effective output which serves as the raw input for the next state. (default: '$')
        """
        self._replace_sagemaker_placeholders(step_type, kwargs)
        if tags:
            self.set_tags_config(tags, kwargs[Field.Parameters.value], step_type)

        super(SageMakerTask, self).__init__(state_id, **kwargs)


    def allowed_fields(self):
        sagemaker_fields = [
            # ProcessingStep: Processor
            Field.Role,
            Field.ImageUri,
            Field.InstanceCount,
            Field.InstanceType,
            Field.Entrypoint,
            Field.VolumeSizeInGB,
            Field.VolumeKMSKey,
            Field.OutputKMSKey,
            Field.MaxRuntimeInSeconds,
            Field.Env,
            Field.Tags,
        ]

        return super(SageMakerTask, self).allowed_fields() + sagemaker_fields


    def _replace_sagemaker_placeholders(self, step_type, args):
        # Fetch path from type
        sagemaker_parameters = args[Field.Parameters.value]
        paths = placeholder_paths.get(step_type)
        treated_args = []

        for arg_name, value in args.items():
            if arg_name in [Field.Parameters.value]:
                continue
            if arg_name in paths.keys():
                path = paths.get(arg_name)
                if self._set_placeholder(sagemaker_parameters, path, value, arg_name):
                    treated_args.append(arg_name)

        SageMakerTask.remove_treated_args(treated_args, args)

    @staticmethod
    def get_value_from_path(parameters, path):
        value_from_path = reduce(operator.getitem, path, parameters)
        return value_from_path
        # return reduce(operator.getitem, path, parameters)

    @staticmethod
    def _set_placeholder(parameters, path, value, arg_name):
        is_set = False
        try:
            SageMakerTask.get_value_from_path(parameters, path[:-1])[path[-1]] = value
            is_set = True
        except KeyError as e:
            message = f"Invalid path {path} for {arg_name}: {e}"
            raise InvalidPathToPlaceholderParameter(message)
        return is_set

    @staticmethod
    def remove_treated_args(treated_args, args):
        for treated_arg in treated_args:
            try:
                del args[treated_arg]
            except KeyError as e:
                pass

    def set_tags_config(self, tags, parameters, step_type):
        if isinstance(tags, Placeholder):
            # Replace with placeholder
            path = placeholder_paths.get(step_type).get(Field.Tags.value)
            if path:
                self._set_placeholder(parameters, path, tags, Field.Tags.value)
        else:
            parameters['Tags'] = tags_dict_to_kv_list(tags)


class TrainingStep(Task):

    """
    Creates a Task State to execute a `SageMaker Training Job <https://docs.aws.amazon.com/sagemaker/latest/dg/API_CreateTrainingJob.html>`_. The TrainingStep will also create a model by default, and the model shares the same name as the training job.
    """

    def __init__(self, state_id, estimator, job_name, data=None, hyperparameters=None, mini_batch_size=None, experiment_config=None, wait_for_completion=True, tags=None, output_data_config_path=None, **kwargs):
        """
        Args:
            state_id (str): State name whose length **must be** less than or equal to 128 unicode characters. State names **must be** unique within the scope of the whole state machine.
            estimator (sagemaker.estimator.EstimatorBase): The estimator for the training step. Can be a `BYO estimator, Framework estimator <https://docs.aws.amazon.com/sagemaker/latest/dg/your-algorithms.html>`_ or `Amazon built-in algorithm estimator <https://docs.aws.amazon.com/sagemaker/latest/dg/algos.html>`_.
            job_name (str or Placeholder): Specify a training job name, this is required for the training job to run. We recommend to use :py:class:`~stepfunctions.inputs.ExecutionInput` placeholder collection to pass the value dynamically in each execution.
            data: Information about the training data. Please refer to the ``fit()`` method of the associated estimator, as this can take any of the following forms:

                * (str or Placeholder) - The S3 location where training data is saved.
                * (dict[str, str] or dict[str, sagemaker.inputs.TrainingInput]) - If using multiple
                    channels for training data, you can specify a dict mapping channel names to
                    strings or :func:`~sagemaker.inputs.TrainingInput` objects.
                * (sagemaker.inputs.TrainingInput) - Channel configuration for S3 data sources that can
                    provide additional information about the training dataset. See
                    :func:`sagemaker.inputs.TrainingInput` for full details.
                * (sagemaker.amazon.amazon_estimator.RecordSet) - A collection of
                    Amazon :class:`Record` objects serialized and stored in S3.
                    For use with an estimator for an Amazon algorithm.
                * (list[sagemaker.amazon.amazon_estimator.RecordSet]) - A list of
                    :class:`sagemaker.amazon.amazon_estimator.RecordSet` objects,
                    where each instance is a different channel of training data.
            hyperparameters (dict, optional): Parameters used for training.
                    Hyperparameters supplied will be merged with the Hyperparameters specified in the estimator.
                    If there are duplicate entries, the value provided through this property will be used. (Default: Hyperparameters specified in the estimator.)
            mini_batch_size (int): Specify this argument only when estimator is a built-in estimator of an Amazon algorithm. For other estimators, batch size should be specified in the estimator.
            experiment_config (dict, optional): Specify the experiment config for the training. (Default: None)
            wait_for_completion (bool, optional): Boolean value set to `True` if the Task state should wait for the training job to complete before proceeding to the next step in the workflow. Set to `False` if the Task state should submit the training job and proceed to the next step. (default: True)
            tags (list[dict], optional): `List to tags <https://docs.aws.amazon.com/sagemaker/latest/dg/API_Tag.html>`_ to associate with the resource.
            output_data_config_path (str or Placeholder, optional): S3 location for saving the training result (model
                artifacts and output files). If specified, it overrides the `output_path` property of `estimator`.
        """
        self.estimator = estimator
        self.job_name = job_name

        if wait_for_completion:
            """
            Example resource arn: arn:aws:states:::sagemaker:createTrainingJob.sync
            """

            kwargs[Field.Resource.value] = get_service_integration_arn(SAGEMAKER_SERVICE_NAME,
                                                                       SageMakerApi.CreateTrainingJob,
                                                                       IntegrationPattern.WaitForCompletion)
        else:
            """
            Example resource arn: arn:aws:states:::sagemaker:createTrainingJob
            """

            kwargs[Field.Resource.value] = get_service_integration_arn(SAGEMAKER_SERVICE_NAME,
                                                                       SageMakerApi.CreateTrainingJob)
        # Convert `data` Placeholder to a JSONPath string because sagemaker.workflow.airflow.training_config does not
        # accept Placeholder in the `input` argument. We will suffix the 'S3Uri' key in `parameters` with ".$" later.
        is_data_placeholder = isinstance(data, Placeholder)
        if is_data_placeholder:
            data = data.to_jsonpath()

        if isinstance(job_name, str):
            parameters = training_config(estimator=estimator, inputs=data, job_name=job_name, mini_batch_size=mini_batch_size)
        else:
            parameters = training_config(estimator=estimator, inputs=data, mini_batch_size=mini_batch_size)

        if estimator.debugger_hook_config != None and estimator.debugger_hook_config is not False:
            parameters['DebugHookConfig'] = estimator.debugger_hook_config._to_request_dict()

        if estimator.rules != None:
            parameters['DebugRuleConfigurations'] = [rule.to_debugger_rule_config_dict() for rule in estimator.rules]

        if isinstance(job_name, Placeholder):
            parameters['TrainingJobName'] = job_name

        if output_data_config_path is not None:
            parameters['OutputDataConfig']['S3OutputPath'] = output_data_config_path

        if data is not None and is_data_placeholder:
            # Replace the 'S3Uri' key with one that supports JSONpath value.
            # Support for uri str only: The list will only contain 1 element
            data_uri = parameters['InputDataConfig'][0]['DataSource']['S3DataSource'].pop('S3Uri', None)
            parameters['InputDataConfig'][0]['DataSource']['S3DataSource']['S3Uri.$'] = data_uri

        if hyperparameters is not None:
            if estimator.hyperparameters() is not None:
                hyperparameters = self.__merge_hyperparameters(hyperparameters, estimator.hyperparameters())
            parameters['HyperParameters'] = hyperparameters

        if experiment_config is not None:
            parameters['ExperimentConfig'] = experiment_config

        if 'S3Operations' in parameters:
            del parameters['S3Operations']

        if tags:
            parameters['Tags'] = tags_dict_to_kv_list(tags)

        kwargs[Field.Parameters.value] = parameters
        super(TrainingStep, self).__init__(state_id, **kwargs)

    def get_expected_model(self, model_name=None):
        """
            Build Sagemaker model representation of the expected trained model from the Training step. This can be passed
            to the ModelStep to save the trained model in Sagemaker.
            Args:
                model_name (str, optional): Specify a model name. If not provided, training job name will be used as the model name.
            Returns:
                sagemaker.model.Model: Sagemaker model representation of the expected trained model.
        """
        model = self.estimator.create_model()
        if model_name:
            model.name = model_name
        else:
            model.name = self.job_name
        model.model_data = self.output()["ModelArtifacts"]["S3ModelArtifacts"]
        return model

    """
    Merges the hyperparameters supplied in the TrainingStep constructor with the hyperparameters
    specified in the estimator. If there are duplicate entries, the value provided in the constructor
    will be used.
    """

    def __merge_hyperparameters(self, training_step_hyperparameters, estimator_hyperparameters):
        """
        Args:
            training_step_hyperparameters (dict): Hyperparameters supplied in the training step constructor
            estimator_hyperparameters (dict): Hyperparameters specified in the estimator
        """
        merged_hyperparameters = estimator_hyperparameters.copy()
        for key, value in training_step_hyperparameters.items():
            if key in merged_hyperparameters:
                logger.info(
                    f"hyperparameter property: <{key}> with value: <{merged_hyperparameters[key]}> provided in the"
                    f" estimator will be overwritten with value provided in constructor: <{value}>")
            merged_hyperparameters[key] = value
        return merged_hyperparameters

class TransformStep(Task):

    """
    Creates a Task State to execute a `SageMaker Transform Job <https://docs.aws.amazon.com/sagemaker/latest/dg/API_CreateTransformJob.html>`_.
    """

    def __init__(self, state_id, transformer, job_name, model_name, data, data_type='S3Prefix', content_type=None, compression_type=None, split_type=None, experiment_config=None, wait_for_completion=True, tags=None, input_filter=None, output_filter=None, join_source=None, **kwargs):
        """
        Args:
            state_id (str): State name whose length **must be** less than or equal to 128 unicode characters. State names **must be** unique within the scope of the whole state machine.
            transformer (sagemaker.transformer.Transformer): The SageMaker transformer to use in the TransformStep.
            job_name (str or Placeholder): Specify a transform job name. We recommend to use :py:class:`~stepfunctions.inputs.ExecutionInput` placeholder collection to pass the value dynamically in each execution.
            model_name (str or Placeholder): Specify a model name for the transform job to use. We recommend to use :py:class:`~stepfunctions.inputs.ExecutionInput` placeholder collection to pass the value dynamically in each execution.
            data (str): Input data location in S3.
            data_type (str): What the S3 location defines (default: 'S3Prefix').
                Valid values:

                * 'S3Prefix' - the S3 URI defines a key name prefix. All objects with this prefix will
                    be used as inputs for the transform job.
                * 'ManifestFile' - the S3 URI points to a single manifest file listing each S3 object
                    to use as an input for the transform job.
            content_type (str): MIME type of the input data (default: None).
            compression_type (str): Compression type of the input data, if compressed (default: None). Valid values: 'Gzip', None.
            split_type (str): The record delimiter for the input object (default: 'None'). Valid values: 'None', 'Line', 'RecordIO', and 'TFRecord'.
            experiment_config (dict, optional): Specify the experiment config for the transform. (Default: None)
            wait_for_completion(bool, optional): Boolean value set to `True` if the Task state should wait for the transform job to complete before proceeding to the next step in the workflow. Set to `False` if the Task state should submit the transform job and proceed to the next step. (default: True)
            tags (list[dict], optional): `List to tags <https://docs.aws.amazon.com/sagemaker/latest/dg/API_Tag.html>`_ to associate with the resource.
            input_filter (str): A JSONPath to select a portion of the input to pass to the algorithm container for inference. If you omit the field, it gets the value ‘$’, representing the entire input. For CSV data, each row is taken as a JSON array, so only index-based JSONPaths can be applied, e.g. $[0], $[1:]. CSV data should follow the RFC format. See Supported JSONPath Operators for a table of supported JSONPath operators. For more information, see the SageMaker API documentation for CreateTransformJob. Some examples: “$[1:]”, “$.features” (default: None).
            output_filter (str): A JSONPath to select a portion of the joined/original output to return as the output. For more information, see the SageMaker API documentation for CreateTransformJob. Some examples: “$[1:]”, “$.prediction” (default: None).
            join_source (str): The source of data to be joined to the transform output. It can be set to ‘Input’ meaning the entire input record will be joined to the inference result. You can use OutputFilter to select the useful portion before uploading to S3. (default: None). Valid values: Input, None.
        """
        if wait_for_completion:
            """
            Example resource arn: arn:aws:states:::sagemaker:createTransformJob.sync
            """

            kwargs[Field.Resource.value] = get_service_integration_arn(SAGEMAKER_SERVICE_NAME,
                                                                       SageMakerApi.CreateTransformJob,
                                                                       IntegrationPattern.WaitForCompletion)
        else:
            """
            Example resource arn: arn:aws:states:::sagemaker:createTransformJob
            """

            kwargs[Field.Resource.value] = get_service_integration_arn(SAGEMAKER_SERVICE_NAME,
                                                                       SageMakerApi.CreateTransformJob)

        if isinstance(job_name, str):
            parameters = transform_config(
                transformer=transformer,
                data=data,
                data_type=data_type,
                content_type=content_type,
                compression_type=compression_type,
                split_type=split_type,
                job_name=job_name,
                input_filter=input_filter,
                output_filter=output_filter,
                join_source=join_source
            )
        else:
            parameters = transform_config(
                transformer=transformer,
                data=data,
                data_type=data_type,
                content_type=content_type,
                compression_type=compression_type,
                split_type=split_type,
                input_filter=input_filter,
                output_filter=output_filter,
                join_source=join_source
            )

        if isinstance(job_name, Placeholder):
            parameters['TransformJobName'] = job_name

        parameters['ModelName'] = model_name

        if experiment_config is not None:
            parameters['ExperimentConfig'] = experiment_config

        if tags:
            parameters['Tags'] = tags_dict_to_kv_list(tags)

        kwargs[Field.Parameters.value] = parameters
        super(TransformStep, self).__init__(state_id, **kwargs)


class ModelStep(Task):

    """
    Creates a Task State to `create a model in SageMaker <https://docs.aws.amazon.com/sagemaker/latest/dg/API_CreateModel.html>`_.
    """

    def __init__(self, state_id, model, model_name=None, instance_type=None, tags=None, **kwargs):
        """
        Args:
            state_id (str): State name whose length **must be** less than or equal to 128 unicode characters. State names **must be** unique within the scope of the whole state machine.
            model (sagemaker.model.Model): The SageMaker model to use in the ModelStep. If :py:class:`TrainingStep` was used to train the model and saving the model is the next step in the workflow, the output of :py:func:`TrainingStep.get_expected_model()` can be passed here.
            model_name (str or Placeholder, optional): Specify a model name, this is required for creating the model. We recommend to use :py:class:`~stepfunctions.inputs.ExecutionInput` placeholder collection to pass the value dynamically in each execution.
            instance_type (str, optional): The EC2 instance type to deploy this Model to. For example, 'ml.p2.xlarge'.
            tags (list[dict], optional): `List to tags <https://docs.aws.amazon.com/sagemaker/latest/dg/API_Tag.html>`_ to associate with the resource.
        """
        if isinstance(model, FrameworkModel):
            parameters = model_config(model=model, instance_type=instance_type, role=model.role, image_uri=model.image_uri)
            if model_name:
                parameters['ModelName'] = model_name
        elif isinstance(model, Model):
            parameters = {
                'ExecutionRoleArn': model.role,
                'ModelName': model_name or model.name,
                'PrimaryContainer': {
                    'Environment': {},
                    'Image': model.image_uri,
                    'ModelDataUrl': model.model_data
                }
            }
        else:
            raise ValueError("Expected 'model' parameter to be of type 'sagemaker.model.Model', but received type '{}'".format(type(model).__name__))

        if 'S3Operations' in parameters:
            del parameters['S3Operations']

        if tags:
            parameters['Tags'] = tags_dict_to_kv_list(tags)

        kwargs[Field.Parameters.value] = parameters

        """
        Example resource arn: arn:aws:states:::sagemaker:createModel
        """

        kwargs[Field.Resource.value] = get_service_integration_arn(SAGEMAKER_SERVICE_NAME,
                                                                   SageMakerApi.CreateModel)

        super(ModelStep, self).__init__(state_id, **kwargs)


class EndpointConfigStep(Task):

    """
    Creates a Task State to `create an endpoint configuration in SageMaker <https://docs.aws.amazon.com/sagemaker/latest/dg/API_CreateEndpointConfig.html>`_.
    """

    def __init__(self, state_id, endpoint_config_name, model_name, initial_instance_count, instance_type, variant_name='AllTraffic', data_capture_config=None, tags=None, **kwargs):
        """
        Args:
            state_id (str): State name whose length **must be** less than or equal to 128 unicode characters. State names **must be** unique within the scope of the whole state machine.
            endpoint_config_name (str or Placeholder): The name of the endpoint configuration to create. We recommend to use :py:class:`~stepfunctions.inputs.ExecutionInput` placeholder collection to pass the value dynamically in each execution.
            model_name (str or Placeholder): The name of the SageMaker model to attach to the endpoint configuration. We recommend to use :py:class:`~stepfunctions.inputs.ExecutionInput` placeholder collection to pass the value dynamically in each execution.
            initial_instance_count (int or Placeholder): The initial number of instances to run in the ``Endpoint`` created from this ``Model``.
            instance_type (str or Placeholder): The EC2 instance type to deploy this Model to. For example, 'ml.p2.xlarge'.
            variant_name (str, optional): The name of the production variant.
            data_capture_config (sagemaker.model_monitor.DataCaptureConfig, optional): Specifies
                configuration related to Endpoint data capture for use with
                Amazon SageMaker Model Monitoring. Default: None.
            tags (list[dict], optional): `List to tags <https://docs.aws.amazon.com/sagemaker/latest/dg/API_Tag.html>`_ to associate with the resource.
        """
        parameters = {
            'EndpointConfigName': endpoint_config_name,
            'ProductionVariants': [{
                'InitialInstanceCount': initial_instance_count,
                'InstanceType': instance_type,
                'ModelName': model_name,
                'VariantName': variant_name
            }]
        }

        if isinstance(data_capture_config, DataCaptureConfig):
            parameters['DataCaptureConfig'] = data_capture_config._to_request_dict()
            
        if tags:
            parameters['Tags'] = tags_dict_to_kv_list(tags)

        """
        Example resource arn: arn:aws:states:::sagemaker:createEndpointConfig
        """

        kwargs[Field.Resource.value] = get_service_integration_arn(SAGEMAKER_SERVICE_NAME,
                                                                   SageMakerApi.CreateEndpointConfig)

        kwargs[Field.Parameters.value] = parameters

        super(EndpointConfigStep, self).__init__(state_id, **kwargs)


class EndpointStep(Task):

    """
    Creates a Task State to `create <https://docs.aws.amazon.com/sagemaker/latest/dg/API_CreateEndpoint.html>`_ or `update <https://docs.aws.amazon.com/sagemaker/latest/dg/API_UpdateEndpoint.html>`_ an endpoint in SageMaker.
    """

    def __init__(self, state_id, endpoint_name, endpoint_config_name, tags=None, update=False, **kwargs):
        """
        Args:
            state_id (str): State name whose length **must be** less than or equal to 128 unicode characters. State names **must be** unique within the scope of the whole state machine.
            endpoint_name (str or Placeholder): The name of the endpoint to create. We recommend to use :py:class:`~stepfunctions.inputs.ExecutionInput` placeholder collection to pass the value dynamically in each execution.
            endpoint_config_name (str or Placeholder): The name of the endpoint configuration to use for the endpoint. We recommend to use :py:class:`~stepfunctions.inputs.ExecutionInput` placeholder collection to pass the value dynamically in each execution.
            tags (list[dict], optional): `List to tags <https://docs.aws.amazon.com/sagemaker/latest/dg/API_Tag.html>`_ to associate with the resource.
            update (bool, optional): Boolean flag set to `True` if endpoint must to be updated. Set to `False` if new endpoint must be created. (default: False)
            tags (list[dict], optional): `List to tags <https://docs.aws.amazon.com/sagemaker/latest/dg/API_Tag.html>`_ to associate with the resource.
        """

        parameters = {
            "EndpointConfigName": endpoint_config_name,
            "EndpointName": endpoint_name,
        }

        if tags:
            parameters['Tags'] = tags_dict_to_kv_list(tags)

        if update:
            """
            Example resource arn: arn:aws:states:::sagemaker:updateEndpoint
            """

            kwargs[Field.Resource.value] = get_service_integration_arn(SAGEMAKER_SERVICE_NAME,
                                                                       SageMakerApi.UpdateEndpoint)
        else:
            """
            Example resource arn: arn:aws:states:::sagemaker:createEndpoint
            """

            kwargs[Field.Resource.value] = get_service_integration_arn(SAGEMAKER_SERVICE_NAME,
                                                                       SageMakerApi.CreateEndpoint)

        kwargs[Field.Parameters.value] = parameters

        super(EndpointStep, self).__init__(state_id, **kwargs)


class TuningStep(Task):

    """
    Creates a Task State to execute a SageMaker HyperParameterTuning Job.
    """

    def __init__(self, state_id, tuner, job_name, data, wait_for_completion=True, tags=None, **kwargs):
        """
        Args:
            state_id (str): State name whose length **must be** less than or equal to 128 unicode characters. State names **must be** unique within the scope of the whole state machine.
            tuner (sagemaker.tuner.HyperparameterTuner): The tuner to use in the TuningStep.
            job_name (str or Placeholder): Specify a tuning job name.  We recommend to use :py:class:`~stepfunctions.inputs.ExecutionInput` placeholder collection to pass the value dynamically in each execution.
            data: Information about the training data. Please refer to the ``fit()`` method of the associated estimator in the tuner, as this can take any of the following forms:

                * (str) - The S3 location where training data is saved.
                * (dict[str, str] or dict[str, sagemaker.inputs.TrainingInput]) - If using multiple
                    channels for training data, you can specify a dict mapping channel names to
                    strings or :func:`~sagemaker.inputs.TrainingInput` objects.
                * (sagemaker.inputs.TrainingInput) - Channel configuration for S3 data sources that can
                    provide additional information about the training dataset. See
                    :func:`sagemaker.inputs.TrainingInput` for full details.
                * (sagemaker.amazon.amazon_estimator.RecordSet) - A collection of
                    Amazon :class:`Record` objects serialized and stored in S3.
                    For use with an estimator for an Amazon algorithm.
                * (list[sagemaker.amazon.amazon_estimator.RecordSet]) - A list of
                    :class:`sagemaker.amazon.amazon_estimator.RecordSet` objects,
                    where each instance is a different channel of training data.
            wait_for_completion(bool, optional): Boolean value set to `True` if the Task state should wait for the tuning job to complete before proceeding to the next step in the workflow. Set to `False` if the Task state should submit the tuning job and proceed to the next step. (default: True)
            tags (list[dict], optional): `List to tags <https://docs.aws.amazon.com/sagemaker/latest/dg/API_Tag.html>`_ to associate with the resource.
        """
        if wait_for_completion:
            """
            Example resource arn: arn:aws:states:::sagemaker:createHyperParameterTuningJob.sync
            """

            kwargs[Field.Resource.value] = get_service_integration_arn(SAGEMAKER_SERVICE_NAME,
                                                                       SageMakerApi.CreateHyperParameterTuningJob,
                                                                       IntegrationPattern.WaitForCompletion)
        else:
            """
            Example resource arn: arn:aws:states:::sagemaker:createHyperParameterTuningJob
            """

            kwargs[Field.Resource.value] = get_service_integration_arn(SAGEMAKER_SERVICE_NAME,
                                                                       SageMakerApi.CreateHyperParameterTuningJob)

        parameters = tuning_config(tuner=tuner, inputs=data, job_name=job_name).copy()

        if job_name is not None:
            parameters['HyperParameterTuningJobName'] = job_name

        if 'S3Operations' in parameters:
            del parameters['S3Operations']

        if tags:
            parameters['Tags'] = tags_dict_to_kv_list(tags)

        kwargs[Field.Parameters.value] = parameters

        super(TuningStep, self).__init__(state_id, **kwargs)


class ProcessingStep(SageMakerTask):

    """
    Creates a Task State to execute a SageMaker Processing Job.

    The following properties can be passed down as kwargs to the sagemaker.processing.Processor to be used dynamically
    in the processing job (compatible with Placeholders): role, image_uri, instance_count, instance_type,
    volume_size_in_gb, volume_kms_key, output_kms_key
    """

    def __init__(self, state_id, processor, job_name, inputs=None, outputs=None, experiment_config=None,
                 container_arguments=None, container_entrypoint=None, kms_key_id=None, wait_for_completion=True,
                 tags=None, max_runtime_in_seconds=None, **kwargs):
        """
        Args:
            state_id (str): State name whose length **must be** less than or equal to 128 unicode characters. State names **must be** unique within the scope of the whole state machine.
            processor (sagemaker.processing.Processor): The processor for the processing step.
            job_name (str or Placeholder): Specify a processing job name, this is required for the processing job to run. We recommend to use :py:class:`~stepfunctions.inputs.ExecutionInput` placeholder collection to pass the value dynamically in each execution.
            inputs (list[:class:`~sagemaker.processing.ProcessingInput`]): Input files for
                the processing job. These must be provided as
                :class:`~sagemaker.processing.ProcessingInput` objects (default: None).
            outputs (list[:class:`~sagemaker.processing.ProcessingOutput`]): Outputs for
                the processing job. These can be specified as either path strings or
                :class:`~sagemaker.processing.ProcessingOutput` objects (default: None).
            experiment_config (dict, optional): Specify the experiment config for the processing. (Default: None)
            container_arguments ([str]): The arguments for a container used to run a processing job.
            container_entrypoint ([str]): The entrypoint for a container used to run a processing job.
            kms_key_id (str): The AWS Key Management Service (AWS KMS) key that Amazon SageMaker
                uses to encrypt the processing job output. KmsKeyId can be an ID of a KMS key,
                ARN of a KMS key, alias of a KMS key, or alias of a KMS key.
                The KmsKeyId is applied to all outputs.
            wait_for_completion (bool, optional): Boolean value set to `True` if the Task state should wait for the processing job to complete before proceeding to the next step in the workflow. Set to `False` if the Task state should submit the processing job and proceed to the next step. (default: True)
            tags (list[dict] or Placeholder, optional): `List to tags <https://docs.aws.amazon.com/sagemaker/latest/dg/API_Tag.html>`_ to associate with the resource.
            max_runtime_in_seconds (int or Placeholder): Specifies the maximum runtime in seconds for the processing job
        """
        if wait_for_completion:
            """
            Example resource arn: arn:aws:states:::sagemaker:createProcessingJob.sync
            """

            kwargs[Field.Resource.value] = get_service_integration_arn(SAGEMAKER_SERVICE_NAME,
                                                                       SageMakerApi.CreateProcessingJob,
                                                                       IntegrationPattern.WaitForCompletion)
        else:
            """
            Example resource arn: arn:aws:states:::sagemaker:createProcessingJob
            """

            kwargs[Field.Resource.value] = get_service_integration_arn(SAGEMAKER_SERVICE_NAME,
                                                                       SageMakerApi.CreateProcessingJob)

        if isinstance(job_name, str):
            parameters = processing_config(processor=processor, inputs=inputs, outputs=outputs, container_arguments=container_arguments, container_entrypoint=container_entrypoint, kms_key_id=kms_key_id, job_name=job_name)
        else:
            parameters = processing_config(processor=processor, inputs=inputs, outputs=outputs, container_arguments=container_arguments, container_entrypoint=container_entrypoint, kms_key_id=kms_key_id)

        if isinstance(job_name, Placeholder):
            parameters['ProcessingJobName'] = job_name
        
        if experiment_config is not None:
            parameters['ExperimentConfig'] = experiment_config
        
        if 'S3Operations' in parameters:
            del parameters['S3Operations']

        if max_runtime_in_seconds:
            parameters['StoppingCondition'] = ProcessingJob.prepare_stopping_condition(max_runtime_in_seconds)
        
        kwargs[Field.Parameters.value] = parameters

        super(ProcessingStep, self).__init__(state_id, __class__.__name__, tags, **kwargs)
