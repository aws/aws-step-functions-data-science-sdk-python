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

import pytest
import sagemaker
import os

from tests.integ import DATA_DIR, DEFAULT_TIMEOUT_MINUTES
from tests.integ.timeout import timeout
from stepfunctions.template import TrainingPipeline
from sagemaker.pytorch import PyTorch
from sagemaker.sklearn import SKLearn
from tests.integ.utils import (
    state_machine_delete_wait,
    delete_sagemaker_model,
    delete_sagemaker_endpoint_config,
    delete_sagemaker_endpoint,
    get_resource_name_from_arn
)

@pytest.fixture(scope="module")
def torch_estimator(sagemaker_role_arn):
    script_path = os.path.join(DATA_DIR, "pytorch_mnist", "mnist.py")   
    return PyTorch(
        py_version='py3',
        entry_point=script_path,
        role=sagemaker_role_arn,
        framework_version='1.2.0',
        instance_count=1,
        instance_type='ml.m5.large',
        hyperparameters={
            'epochs': 6,
            'backend': 'gloo'
        }
    )

@pytest.fixture(scope="module")
def sklearn_estimator(sagemaker_role_arn):
    script_path = os.path.join(DATA_DIR, "sklearn_mnist", "mnist.py")   
    return SKLearn(
        framework_version='0.20.0',
        py_version='py3',
        entry_point=script_path,
        role=sagemaker_role_arn,
        instance_count=1,
        instance_type='ml.m5.large',
        hyperparameters={
            "epochs": 1
        }
    )


def _get_endpoint_name(execution_output):
    endpoint_arn = execution_output.get('EndpointArn', None)
    endpoint_name = None

    if endpoint_arn is not None:
        resource_name = get_resource_name_from_arn(endpoint_arn)
        endpoint_name = resource_name.split("/")[-1]
    
    return endpoint_name


def _pipeline_test_suite(sagemaker_client, training_job_name, model_name, endpoint_name):
    assert sagemaker_client.describe_training_job(TrainingJobName=training_job_name).get('TrainingJobName') == training_job_name
    assert sagemaker_client.describe_model(ModelName=model_name).get('ModelName') == endpoint_name
    assert sagemaker_client.describe_endpoint(EndpointName=endpoint_name).get('EndpointName') == endpoint_name


def _pipeline_teardown(sfn_client, sagemaker_session, endpoint_name, pipeline):
    if endpoint_name is not None:
        delete_sagemaker_endpoint(endpoint_name, sagemaker_session)
        delete_sagemaker_endpoint_config(endpoint_name, sagemaker_session)
        delete_sagemaker_model(endpoint_name, sagemaker_session)

    state_machine_delete_wait(sfn_client, pipeline.workflow.state_machine_arn)


def test_torch_training_pipeline(sfn_client, sagemaker_client, torch_estimator, sagemaker_session, sfn_role_arn):
    with timeout(minutes=DEFAULT_TIMEOUT_MINUTES):
        # upload input data
        data_path = os.path.join(DATA_DIR, "pytorch_mnist")
        inputs = sagemaker_session.upload_data(
            path=data_path, 
            bucket=sagemaker_session.default_bucket(), 
            key_prefix='integ-test-data/torch_mnist/train'
        )

        # create training pipeline
        pipeline = TrainingPipeline(
            torch_estimator, 
            sfn_role_arn, 
            inputs, 
            sagemaker_session.default_bucket(), 
            sfn_client
        )
        pipeline.create()
        # execute pipeline
        execution = pipeline.execute()

        # get pipeline output and extract endpoint name
        execution_output = execution.get_output(wait=True)
        assert execution_output  # If fails, execution_output is None.

        endpoint_name = _get_endpoint_name(execution_output)

        # assertions
        _pipeline_test_suite(sagemaker_client, training_job_name='estimator-'+endpoint_name, model_name=endpoint_name, endpoint_name=endpoint_name)

        # teardown
        _pipeline_teardown(sfn_client, sagemaker_session, endpoint_name, pipeline)


def test_sklearn_training_pipeline(sfn_client, sagemaker_client, sklearn_estimator, sagemaker_session, sfn_role_arn):
    with timeout(minutes=DEFAULT_TIMEOUT_MINUTES):
        # upload input data
        data_path = os.path.join(DATA_DIR, "sklearn_mnist")
        inputs = sagemaker_session.upload_data(
            path=os.path.join(data_path, "train"),
            bucket=sagemaker_session.default_bucket(),
            key_prefix="integ-test-data/sklearn_mnist/train"
        )

        # create training pipeline
        pipeline = TrainingPipeline(
            sklearn_estimator, 
            sfn_role_arn, 
            inputs, 
            sagemaker_session.default_bucket(), 
            sfn_client
        )
        pipeline.create()
        # run pipeline
        execution = pipeline.execute()
        
        # get pipeline output and extract endpoint name
        execution_output = execution.get_output(wait=True)
        assert execution_output  # If fails, execution_output is None.

        endpoint_name = _get_endpoint_name(execution_output)

        # assertions
        _pipeline_test_suite(sagemaker_client, training_job_name='estimator-'+endpoint_name, model_name=endpoint_name, endpoint_name=endpoint_name)

        # teardown
        _pipeline_teardown(sfn_client, sagemaker_session, endpoint_name, pipeline)