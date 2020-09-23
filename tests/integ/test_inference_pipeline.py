# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License").
# You may not use this file except in compliance with the License.
# A copy of the License is located at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# or in the "license" file accompanying this file. This file is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied. See the License for the specific language governing
# permissions and limitations under the License.

from __future__ import absolute_import

import os
import json
import pytest
from datetime import datetime

from sagemaker.sklearn.estimator import SKLearn

from stepfunctions.template.pipeline import InferencePipeline

from tests.integ import DATA_DIR, DEFAULT_TIMEOUT_MINUTES
from tests.integ.timeout import timeout
from tests.integ.utils import (
    state_machine_delete_wait,
    delete_sagemaker_model,
    delete_sagemaker_endpoint_config,
    delete_sagemaker_endpoint,
)


# Constants
BASE_NAME = 'inference-pipeline-integtest'
COMPRESSED_NPY_DATA = 'mnist.npy.gz'

# Fixtures
@pytest.fixture(scope="module")
def sklearn_preprocessor(sagemaker_role_arn, sagemaker_session):
    script_path = os.path.join(DATA_DIR,
                               'one_p_mnist',
                               'sklearn_mnist_preprocessor.py')
    sklearn_preprocessor = SKLearn(
        framework_version='0.20.0',
        py_version='py3',
        entry_point=script_path,
        role=sagemaker_role_arn,
        instance_type="ml.m5.large",
        sagemaker_session=sagemaker_session,
        hyperparameters={"epochs": 1},
    )
    return sklearn_preprocessor


@pytest.fixture(scope="module")
def sklearn_estimator(sagemaker_role_arn, sagemaker_session):
    script_path = os.path.join(DATA_DIR,
                               'one_p_mnist',
                               'sklearn_mnist_estimator.py')
    sklearn_estimator = SKLearn(
        framework_version='0.20.0',
        py_version='py3',
        entry_point=script_path,
        role=sagemaker_role_arn,
        instance_type="ml.m5.large",
        sagemaker_session=sagemaker_session,
        hyperparameters={"epochs": 1},
        input_mode='File'
    )
    return sklearn_estimator


@pytest.fixture(scope="module")
def inputs(sagemaker_session):
    data_path = os.path.join(DATA_DIR, "one_p_mnist", COMPRESSED_NPY_DATA)
    inputs = sagemaker_session.upload_data(
        path=data_path, key_prefix='dataset/one_p_mnist'
    )
    return inputs


def test_inference_pipeline_framework(
        sfn_client,
        sagemaker_session,
        sfn_role_arn,
        sagemaker_role_arn,
        sklearn_preprocessor,
        sklearn_estimator,
        inputs):
    bucket_name = sagemaker_session.default_bucket()
    unique_name = '{}-{}'.format(BASE_NAME, datetime.now().strftime('%Y%m%d%H%M%S'))
    with timeout(minutes=DEFAULT_TIMEOUT_MINUTES):
        pipeline = InferencePipeline(
            preprocessor=sklearn_preprocessor,
            estimator=sklearn_estimator,
            inputs={'train': inputs, 'test': inputs},
            s3_bucket=bucket_name,
            role=sfn_role_arn,
            compression_type='Gzip',
            content_type='application/x-npy',
            pipeline_name=unique_name
        )

        _ = pipeline.create()
        execution = pipeline.execute(job_name=unique_name)
        out = execution.get_output(wait=True)
        assert out  # If fails, out is None.

        execution_info = execution.describe()

        execution_arn = execution.execution_arn
        state_machine_definition = sfn_client.describe_state_machine_for_execution(executionArn=execution_arn)
        state_machine_definition['definition'] = json.loads(state_machine_definition['definition'])
        assert state_machine_definition['definition'] == pipeline.workflow.definition.to_dict()

        state_machine_arn = state_machine_definition['stateMachineArn']
        job_name = execution_info['name']

        client_info = sfn_client.describe_execution(executionArn=execution_arn)
        client_info['input'] = json.loads(client_info['input'])
        _ = client_info.pop('ResponseMetadata')
        _ = client_info.pop('output')

        assert client_info['input'] == json.loads(execution_info['input'])

        state_machine_delete_wait(sfn_client, state_machine_arn)
        delete_sagemaker_endpoint(job_name, sagemaker_session)
        delete_sagemaker_endpoint_config(job_name, sagemaker_session)
        delete_sagemaker_model(job_name, sagemaker_session)
