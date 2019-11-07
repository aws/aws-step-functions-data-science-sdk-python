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

from stepfunctions.inputs import ExecutionInput, StepInput
from stepfunctions.steps.states import Task
from stepfunctions.steps.fields import Field
from stepfunctions.steps.utils import tags_dict_to_kv_list

from sagemaker.workflow.airflow import training_config, transform_config, model_config, tuning_config
from sagemaker.model import Model, FrameworkModel


class TrainingStep(Task):

    """
    Creates a Task State to execute a `SageMaker Training Job <https://docs.aws.amazon.com/sagemaker/latest/dg/API_CreateTrainingJob.html>`_. The TrainingStep will also create a model by default, and the model shares the same name as the training job.
    """

    def __init__(self, state_id, estimator, job_name, data=None, hyperparameters=None, mini_batch_size=None, wait_for_completion=True, **kwargs):
        """
        Args:
            state_id (str): State name whose length **must be** less than or equal to 128 unicode characters. State names **must be** unique within the scope of the whole state machine.
            estimator (sagemaker.estimator.EstimatorBase): The estimator for the training step. Can be a `BYO estimator, Framework estimator <https://docs.aws.amazon.com/sagemaker/latest/dg/your-algorithms.html>`_ or `Amazon built-in algorithm estimator <https://docs.aws.amazon.com/sagemaker/latest/dg/algos.html>`_.
            job_name (str or Placeholder): Specify a training job name, this is required for the training job to run. We recommend to use :py:class:`~stepfunctions.inputs.ExecutionInput` placeholder collection to pass the value dynamically in each execution.
            data: Information about the training data. Please refer to the ``fit()`` method of the associated estimator, as this can take any of the following forms:

                * (str) - The S3 location where training data is saved.
                * (dict[str, str] or dict[str, sagemaker.session.s3_input]) - If using multiple
                    channels for training data, you can specify a dict mapping channel names to
                    strings or :func:`~sagemaker.session.s3_input` objects.
                * (sagemaker.session.s3_input) - Channel configuration for S3 data sources that can
                    provide additional information about the training dataset. See
                    :func:`sagemaker.session.s3_input` for full details.
                * (sagemaker.amazon.amazon_estimator.RecordSet) - A collection of
                    Amazon :class:`Record` objects serialized and stored in S3.
                    For use with an estimator for an Amazon algorithm.
                * (list[sagemaker.amazon.amazon_estimator.RecordSet]) - A list of
                    :class:`sagemaker.amazon.amazon_estimator.RecordSet` objects,
                    where each instance is a different channel of training data.
            hyperparameters (dict, optional): Specify the hyper parameters for the training. (Default: None)
            mini_batch_size (int): Specify this argument only when estimator is a built-in estimator of an Amazon algorithm. For other estimators, batch size should be specified in the estimator.
            wait_for_completion (bool, optional): Boolean value set to `True` if the Task state should wait for the training job to complete before proceeding to the next step in the workflow. Set to `False` if the Task state should submit the training job and proceed to the next step. (default: True)
        """
        self.estimator = estimator
        self.job_name = job_name

        if wait_for_completion:
            kwargs[Field.Resource.value] = 'arn:aws:states:::sagemaker:createTrainingJob.sync'
        else:
            kwargs[Field.Resource.value] = 'arn:aws:states:::sagemaker:createTrainingJob'

        if isinstance(job_name, str):
            parameters = training_config(estimator=estimator, inputs=data, job_name=job_name, mini_batch_size=mini_batch_size)
        else:
            parameters = training_config(estimator=estimator, inputs=data, mini_batch_size=mini_batch_size)

        if isinstance(job_name, (ExecutionInput, StepInput)):
            parameters['TrainingJobName'] = job_name

        if hyperparameters is not None:
            parameters['HyperParameters'] = hyperparameters

        if 'S3Operations' in parameters:
            del parameters['S3Operations']

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


class TransformStep(Task):

    """
    Creates a Task State to execute a `SageMaker Transform Job <https://docs.aws.amazon.com/sagemaker/latest/dg/API_CreateTransformJob.html>`_.
    """

    def __init__(self, state_id, transformer, job_name, model_name, data, data_type='S3Prefix', content_type=None, compression_type=None, split_type=None, wait_for_completion=True, **kwargs):
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
            wait_for_completion(bool, optional): Boolean value set to `True` if the Task state should wait for the transform job to complete before proceeding to the next step in the workflow. Set to `False` if the Task state should submit the transform job and proceed to the next step. (default: True)
        """
        if wait_for_completion:
            kwargs[Field.Resource.value] = 'arn:aws:states:::sagemaker:createTransformJob.sync'
        else:
            kwargs[Field.Resource.value] = 'arn:aws:states:::sagemaker:createTransformJob'

        if isinstance(job_name, str):
            parameters = transform_config(
                transformer=transformer,
                data=data,
                data_type=data_type,
                content_type=content_type,
                compression_type=compression_type,
                split_type=split_type,
                job_name=job_name
            )
        else:
            parameters = transform_config(
                transformer=transformer,
                data=data,
                data_type=data_type,
                content_type=content_type,
                compression_type=compression_type,
                split_type=split_type
            )

        if isinstance(job_name, (ExecutionInput, StepInput)):
            parameters['TransformJobName'] = job_name

        parameters['ModelName'] = model_name

        kwargs[Field.Parameters.value] = parameters
        super(TransformStep, self).__init__(state_id, **kwargs)


class ModelStep(Task):

    """
    Creates a Task State to `create a model in SageMaker <https://docs.aws.amazon.com/sagemaker/latest/dg/API_CreateModel.html>`_.
    """

    def __init__(self, state_id, model, model_name=None, instance_type=None, **kwargs):
        """
        Args:
            state_id (str): State name whose length **must be** less than or equal to 128 unicode characters. State names **must be** unique within the scope of the whole state machine.
            model (sagemaker.model.Model): The SageMaker model to use in the ModelStep. If :py:class:`TrainingStep` was used to train the model and saving the model is the next step in the workflow, the output of :py:func:`TrainingStep.get_expected_model()` can be passed here.
            model_name (str or Placeholder, optional): Specify a model name, this is required for creating the model. We recommend to use :py:class:`~stepfunctions.inputs.ExecutionInput` placeholder collection to pass the value dynamically in each execution.
            instance_type (str, optional): The EC2 instance type to deploy this Model to. For example, 'ml.p2.xlarge'. This parameter is typically required when the estimator used is not an `Amazon built-in algorithm <https://docs.aws.amazon.com/sagemaker/latest/dg/algos.html>`_.
        """
        if isinstance(model, FrameworkModel):
            parameters = model_config(model=model, instance_type=instance_type, role=model.role, image=model.image)
            if model_name:
                parameters['ModelName'] = model_name
        elif isinstance(model, Model):
            parameters = {
                'ExecutionRoleArn': model.role,
                'ModelName': model_name or model.name,
                'PrimaryContainer': {
                    'Environment': {},
                    'Image': model.image,
                    'ModelDataUrl': model.model_data
                }
            }
        else:
            raise ValueError("Expected 'model' parameter to be of type 'sagemaker.model.Model', but received type '{}'".format(type(model).__name__))

        kwargs[Field.Parameters.value] = parameters
        kwargs[Field.Resource.value] = 'arn:aws:states:::sagemaker:createModel'

        super(ModelStep, self).__init__(state_id, **kwargs)


class EndpointConfigStep(Task):

    """
    Creates a Task State to `create an endpoint configuration in SageMaker <https://docs.aws.amazon.com/sagemaker/latest/dg/API_CreateEndpointConfig.html>`_.
    """

    def __init__(self, state_id, endpoint_config_name, model_name, initial_instance_count, instance_type, tags=None, **kwargs):
        """
        Args:
            state_id (str): State name whose length **must be** less than or equal to 128 unicode characters. State names **must be** unique within the scope of the whole state machine.
            endpoint_config_name (str or Placeholder): The name of the endpoint configuration to create. We recommend to use :py:class:`~stepfunctions.inputs.ExecutionInput` placeholder collection to pass the value dynamically in each execution.
            model_name (str or Placeholder): The name of the SageMaker model to attach to the endpoint configuration. We recommend to use :py:class:`~stepfunctions.inputs.ExecutionInput` placeholder collection to pass the value dynamically in each execution.
            initial_instance_count (int or Placeholder): The initial number of instances to run in the ``Endpoint`` created from this ``Model``.
            instance_type (str or Placeholder): The EC2 instance type to deploy this Model to. For example, 'ml.p2.xlarge'.
            tags (list[dict], optional): `List to tags <https://docs.aws.amazon.com/sagemaker/latest/dg/API_Tag.html>`_ to associate with the resource.
        """
        parameters = {
            'EndpointConfigName': endpoint_config_name,
            'ProductionVariants': [{
                'InitialInstanceCount': initial_instance_count,
                'InstanceType': instance_type,
                'ModelName': model_name,
                'VariantName': 'AllTraffic'
            }]
        }

        if tags:
            parameters['Tags'] = tags_dict_to_kv_list(tags)

        kwargs[Field.Resource.value] = 'arn:aws:states:::sagemaker:createEndpointConfig'
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
        """

        parameters = {
            "EndpointConfigName": endpoint_config_name,
            "EndpointName": endpoint_name,
        }

        if tags:
            parameters['Tags'] = tags_dict_to_kv_list(tags)

        if update:
            kwargs[Field.Resource.value] = 'arn:aws:states:::sagemaker:updateEndpoint'
        else:
            kwargs[Field.Resource.value] = 'arn:aws:states:::sagemaker:createEndpoint'

        kwargs[Field.Parameters.value] = parameters

        super(EndpointStep, self).__init__(state_id, **kwargs)


class TuningStep(Task):

    """
    Creates a Task State to execute a SageMaker HyperParameterTuning Job.
    """

    def __init__(self, state_id, tuner, job_name, data, wait_for_completion=True, **kwargs):
        """
        Args:
            state_id (str): State name whose length **must be** less than or equal to 128 unicode characters. State names **must be** unique within the scope of the whole state machine.
            tuner (sagemaker.tuner.HyperparameterTuner): The tuner to use in the TuningStep.
            job_name (str or Placeholder): Specify a tuning job name.  We recommend to use :py:class:`~stepfunctions.inputs.ExecutionInput` placeholder collection to pass the value dynamically in each execution.
            data: Information about the training data. Please refer to the ``fit()`` method of the associated estimator in the tuner, as this can take any of the following forms:

                * (str) - The S3 location where training data is saved.
                * (dict[str, str] or dict[str, sagemaker.session.s3_input]) - If using multiple
                    channels for training data, you can specify a dict mapping channel names to
                    strings or :func:`~sagemaker.session.s3_input` objects.
                * (sagemaker.session.s3_input) - Channel configuration for S3 data sources that can
                    provide additional information about the training dataset. See
                    :func:`sagemaker.session.s3_input` for full details.
                * (sagemaker.amazon.amazon_estimator.RecordSet) - A collection of
                    Amazon :class:`Record` objects serialized and stored in S3.
                    For use with an estimator for an Amazon algorithm.
                * (list[sagemaker.amazon.amazon_estimator.RecordSet]) - A list of
                    :class:`sagemaker.amazon.amazon_estimator.RecordSet` objects,
                    where each instance is a different channel of training data.
            wait_for_completion(bool, optional): Boolean value set to `True` if the Task state should wait for the tuning job to complete before proceeding to the next step in the workflow. Set to `False` if the Task state should submit the tuning job and proceed to the next step. (default: True)
        """
        if wait_for_completion:
            kwargs[Field.Resource.value] = 'arn:aws:states:::sagemaker:createHyperParameterTuningJob.sync'
        else:
            kwargs[Field.Resource.value] = 'arn:aws:states:::sagemaker:createHyperParameterTuningJob'

        parameters = tuning_config(tuner=tuner, inputs=data, job_name=job_name).copy()

        if job_name is not None:
            parameters['HyperParameterTuningJobName'] = job_name

        if 'S3Operations' in parameters:
            del parameters['S3Operations']

        kwargs[Field.Parameters.value] = parameters

        super(TuningStep, self).__init__(state_id, **kwargs)
