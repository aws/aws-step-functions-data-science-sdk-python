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

import os
import sys
import pickle
import json
import pytest
import gzip
import uuid

import boto3

from sagemaker import KMeans
from sagemaker.amazon import pca
from sagemaker.utils import unique_name_from_base
from sagemaker.parameter import IntegerParameter, CategoricalParameter
from sagemaker.tuner import HyperparameterTuner
from sagemaker.processing import ProcessingInput, ProcessingOutput

from stepfunctions.steps import Chain
from stepfunctions.steps.sagemaker import TrainingStep, TransformStep, ModelStep, EndpointStep, EndpointConfigStep, TuningStep, ProcessingStep
from stepfunctions.workflow import Workflow

from tests.integ import DATA_DIR, DEFAULT_TIMEOUT_MINUTES
from tests.integ.timeout import timeout
from tests.integ.utils import (
    state_machine_delete_wait,
    delete_sagemaker_model,
    delete_sagemaker_endpoint_config,
    delete_sagemaker_endpoint,
    get_resource_name_from_arn
)

INSTANCE_COUNT = 1
INSTANCE_TYPE = "ml.m5.large"


@pytest.fixture(scope="module")
def trained_estimator(pca_estimator_fixture, record_set_fixture):
    job_name = unique_name_from_base("integ-test-sagemaker-steps-reuse-training-job")
    pca_estimator_fixture.fit(records=record_set_fixture, mini_batch_size=200, wait=True, job_name=job_name)
    return pca_estimator_fixture

@pytest.fixture(scope="module")
def record_set_for_hyperparameter_tuning(train_set, pca_estimator_fixture):
    train_record_set = pca_estimator_fixture.record_set(train=train_set[0][:100])
    test_record_set = pca_estimator_fixture.record_set(train_set[0][:100], channel="test")
    return  [train_record_set, test_record_set]

def generate_job_name():
    return uuid.uuid1().hex

def create_workflow_and_check_definition(workflow_graph, workflow_name, sfn_client, sfn_role_arn):
    # Create workflow
    workflow = Workflow(
        name=workflow_name,
        definition=workflow_graph,
        role=sfn_role_arn,
        client=sfn_client
    )
    state_machine_arn = workflow.create()

    # Check workflow definition
    state_machine_desc = sfn_client.describe_state_machine(stateMachineArn=state_machine_arn)
    assert workflow.definition.to_dict() == json.loads(state_machine_desc.get('definition'))

    return workflow

def test_training_step(pca_estimator_fixture, record_set_fixture, sfn_client, sfn_role_arn):
    # Build workflow definition
    job_name = generate_job_name()
    training_step = TrainingStep('create_training_job_step', estimator=pca_estimator_fixture, job_name=job_name, data=record_set_fixture, mini_batch_size=200)
    workflow_graph = Chain([training_step])

    with timeout(minutes=DEFAULT_TIMEOUT_MINUTES):
        # Create workflow and check definition
        workflow = create_workflow_and_check_definition(
            workflow_graph=workflow_graph,
            workflow_name=unique_name_from_base("integ-test-training-step-workflow"),
            sfn_client=sfn_client,
            sfn_role_arn=sfn_role_arn
        )

        # Execute workflow
        execution = workflow.execute()
        execution_output = execution.get_output(wait=True)

        # Check workflow output
        assert execution_output.get("TrainingJobStatus") == "Completed"

        # Cleanup
        state_machine_delete_wait(sfn_client, workflow.state_machine_arn)
        # End of Cleanup

def test_model_step(trained_estimator, sfn_client, sagemaker_session, sfn_role_arn):
    # Build workflow definition
    model_name = generate_job_name()
    model_step = ModelStep('create_model_step', model=trained_estimator.create_model(), model_name=model_name)
    workflow_graph = Chain([model_step])

    with timeout(minutes=DEFAULT_TIMEOUT_MINUTES):
        # Create workflow and check definition
        workflow = create_workflow_and_check_definition(
            workflow_graph=workflow_graph,
            workflow_name=unique_name_from_base("integ-test-model-step-workflow"),
            sfn_client=sfn_client,
            sfn_role_arn=sfn_role_arn
        )

        # Execute workflow
        execution = workflow.execute()
        execution_output = execution.get_output(wait=True)

        # Check workflow output
        assert execution_output.get("ModelArn") is not None
        assert execution_output["SdkHttpMetadata"]["HttpStatusCode"] == 200

        # Cleanup
        state_machine_delete_wait(sfn_client, workflow.state_machine_arn)
        model_name = get_resource_name_from_arn(execution_output.get("ModelArn")).split("/")[1]
        delete_sagemaker_model(model_name, sagemaker_session)
        # End of Cleanup

def test_transform_step(trained_estimator, sfn_client, sfn_role_arn):
    # Create transformer from previously created estimator
    job_name = generate_job_name()
    pca_transformer = trained_estimator.transformer(instance_count=INSTANCE_COUNT, instance_type=INSTANCE_TYPE)

    # Create a model step to save the model
    model_step = ModelStep('create_model_step', model=trained_estimator.create_model(), model_name=job_name)

    # Upload data for transformation to S3
    data_path = os.path.join(DATA_DIR, "one_p_mnist")
    transform_input_path = os.path.join(data_path, "transform_input.csv")
    transform_input_key_prefix = "integ-test-data/one_p_mnist/transform"
    transform_input = pca_transformer.sagemaker_session.upload_data(
        path=transform_input_path, key_prefix=transform_input_key_prefix
    )

    # Build workflow definition
    transform_step = TransformStep('create_transform_job_step', pca_transformer, job_name=job_name, model_name=job_name, data=transform_input, content_type="text/csv")
    workflow_graph = Chain([model_step, transform_step])

    with timeout(minutes=DEFAULT_TIMEOUT_MINUTES):
        # Create workflow and check definition
        workflow = create_workflow_and_check_definition(
            workflow_graph=workflow_graph,
            workflow_name=unique_name_from_base("integ-test-transform-step-workflow"),
            sfn_client=sfn_client,
            sfn_role_arn=sfn_role_arn
        )

        # Execute workflow
        execution = workflow.execute()
        execution_output = execution.get_output(wait=True)

        # Check workflow output
        assert execution_output.get("TransformJobStatus") == "Completed"

        # Cleanup
        state_machine_delete_wait(sfn_client, workflow.state_machine_arn)
        # End of Cleanup

def test_endpoint_config_step(trained_estimator, sfn_client, sagemaker_session, sfn_role_arn):
    # Setup: Create model for trained estimator in SageMaker
    model = trained_estimator.create_model()
    model._create_sagemaker_model(instance_type=INSTANCE_TYPE)
    # End of Setup

    # Build workflow definition
    endpoint_config_name = unique_name_from_base("integ-test-endpoint-config")
    endpoint_config_step = EndpointConfigStep('create_endpoint_config_step', endpoint_config_name=endpoint_config_name, model_name=model.name, initial_instance_count=INSTANCE_COUNT, instance_type=INSTANCE_TYPE)
    workflow_graph = Chain([endpoint_config_step])

    with timeout(minutes=DEFAULT_TIMEOUT_MINUTES):
        # Create workflow and check definition
        workflow = create_workflow_and_check_definition(
            workflow_graph=workflow_graph,
            workflow_name=unique_name_from_base("integ-test-create-endpoint-config-step-workflow"),
            sfn_client=sfn_client,
            sfn_role_arn=sfn_role_arn
        )

        # Execute workflow
        execution = workflow.execute()
        execution_output = execution.get_output(wait=True)
        
        # Check workflow output
        assert execution_output.get("EndpointConfigArn") is not None
        assert execution_output["SdkHttpMetadata"]["HttpStatusCode"] == 200

        # Cleanup
        state_machine_delete_wait(sfn_client, workflow.state_machine_arn)
        delete_sagemaker_endpoint_config(endpoint_config_name, sagemaker_session)
        delete_sagemaker_model(model.name, sagemaker_session)
        # End of Cleanup

def test_create_endpoint_step(trained_estimator, record_set_fixture, sfn_client, sagemaker_session, sfn_role_arn):
    # Setup: Create model and endpoint config for trained estimator in SageMaker
    model = trained_estimator.create_model()
    model._create_sagemaker_model(instance_type=INSTANCE_TYPE)
    endpoint_config = model.sagemaker_session.create_endpoint_config(
        name = model.name,
        model_name = model.name,
        initial_instance_count=INSTANCE_COUNT,
        instance_type=INSTANCE_TYPE
    )
    # End of Setup

    # Build workflow definition
    endpoint_name = unique_name_from_base("integ-test-endpoint")
    endpoint_step = EndpointStep('create_endpoint_step', endpoint_name=endpoint_name, endpoint_config_name=model.name)
    workflow_graph = Chain([endpoint_step])

    with timeout(minutes=DEFAULT_TIMEOUT_MINUTES):
        # Create workflow and check definition
        workflow = create_workflow_and_check_definition(
            workflow_graph=workflow_graph,
            workflow_name=unique_name_from_base("integ-test-create-endpoint-step-workflow"),
            sfn_client=sfn_client,
            sfn_role_arn=sfn_role_arn
        )

        # Execute workflow
        execution = workflow.execute()
        execution_output = execution.get_output(wait=True)
        
        # Check workflow output 
        endpoint_arn = execution_output.get("EndpointArn")
        assert execution_output.get("EndpointArn") is not None
        assert execution_output["SdkHttpMetadata"]["HttpStatusCode"] == 200

        # Cleanup
        state_machine_delete_wait(sfn_client, workflow.state_machine_arn)
        delete_sagemaker_endpoint(endpoint_name, sagemaker_session)
        delete_sagemaker_endpoint_config(model.name, sagemaker_session)
        delete_sagemaker_model(model.name, sagemaker_session)
        # End of Cleanup

def test_tuning_step(sfn_client, record_set_for_hyperparameter_tuning, sagemaker_role_arn, sfn_role_arn):
    job_name = generate_job_name()

    kmeans = KMeans(
        role=sagemaker_role_arn,
        train_instance_count=1,
        train_instance_type=INSTANCE_TYPE,
        k=10
    )

    hyperparameter_ranges = {
        "extra_center_factor": IntegerParameter(4, 10),
        "mini_batch_size": IntegerParameter(10, 100),
        "epochs": IntegerParameter(1, 2),
        "init_method": CategoricalParameter(["kmeans++", "random"]),
    }

    tuner = HyperparameterTuner(
        estimator=kmeans,
        objective_metric_name="test:msd",
        hyperparameter_ranges=hyperparameter_ranges,
        objective_type="Minimize",
        max_jobs=2,
        max_parallel_jobs=2,
    )
    
    # Build workflow definition
    tuning_step = TuningStep('Tuning', tuner=tuner, job_name=job_name, data=record_set_for_hyperparameter_tuning)
    workflow_graph = Chain([tuning_step])

    with timeout(minutes=DEFAULT_TIMEOUT_MINUTES):
        # Create workflow and check definition
        workflow = create_workflow_and_check_definition(
            workflow_graph=workflow_graph,
            workflow_name=unique_name_from_base("integ-test-tuning-step-workflow"),
            sfn_client=sfn_client,
            sfn_role_arn=sfn_role_arn
        )

        # Execute workflow
        execution = workflow.execute()
        execution_output = execution.get_output(wait=True)
        
        # Check workflow output 
        assert execution_output.get("HyperParameterTuningJobStatus") == "Completed"

        # Cleanup
        state_machine_delete_wait(sfn_client, workflow.state_machine_arn)
        # End of Cleanup

def test_processing_step(sklearn_processor_fixture, sagemaker_session, sfn_client, sfn_role_arn):
    region = boto3.session.Session().region_name
    input_data = 's3://sagemaker-sample-data-{}/processing/census/census-income.csv'.format(region)

    input_s3 = sagemaker_session.upload_data(
        path=os.path.join(DATA_DIR, 'sklearn_processing'),
        bucket=sagemaker_session.default_bucket(),
        key_prefix='integ-test-data/sklearn_processing/code'
    )

    output_s3 = 's3://' + sagemaker_session.default_bucket() + '/integ-test-data/sklearn_processing'

    inputs = [
        ProcessingInput(source=input_data, destination='/opt/ml/processing/input', input_name='input-1'),
        ProcessingInput(source=input_s3 + '/preprocessor.py', destination='/opt/ml/processing/input/code', input_name='code'),
    ]

    outputs = [
        ProcessingOutput(source='/opt/ml/processing/train', destination=output_s3 + '/train_data', output_name='train_data'),
        ProcessingOutput(source='/opt/ml/processing/test', destination=output_s3 + '/test_data', output_name='test_data'),
    ]

    job_name = generate_job_name()
    processing_step = ProcessingStep('create_processing_job_step',
        processor=sklearn_processor_fixture,
        job_name=job_name,
        inputs=inputs,
        outputs=outputs,
        container_arguments=['--train-test-split-ratio', '0.2'],
        container_entrypoint=['python3', '/opt/ml/processing/input/code/preprocessor.py'],
    )
    workflow_graph = Chain([processing_step])

    with timeout(minutes=DEFAULT_TIMEOUT_MINUTES):
        # Create workflow and check definition
        workflow = create_workflow_and_check_definition(
            workflow_graph=workflow_graph,
            workflow_name=unique_name_from_base("integ-test-processing-step-workflow"),
            sfn_client=sfn_client,
            sfn_role_arn=sfn_role_arn
        )
        
        # Execute workflow
        execution = workflow.execute()
        execution_output = execution.get_output(wait=True)

        # Check workflow output
        assert execution_output.get("ProcessingJobStatus") == "Completed"

        # Cleanup
        state_machine_delete_wait(sfn_client, workflow.state_machine_arn)
        # End of Cleanup
