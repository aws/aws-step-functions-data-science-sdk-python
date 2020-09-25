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
import gzip
import pickle
import pytest
import numpy as np
import json
from datetime import datetime

import boto3

# import Sagemaker
from sagemaker.amazon.pca import PCA
from sagemaker.image_uris import retrieve 

# import StepFunctions
from stepfunctions.template.pipeline import TrainingPipeline

from tests.integ import DATA_DIR, DEFAULT_TIMEOUT_MINUTES
from tests.integ.timeout import timeout
from tests.integ.utils import (
    state_machine_delete_wait,
    delete_sagemaker_model,
    delete_sagemaker_endpoint_config,
    delete_sagemaker_endpoint,
)


# Constants
BASE_NAME = 'training-pipeline-integtest'


# Fixtures
@pytest.fixture(scope="module")
def pca_estimator(sagemaker_role_arn):
    pca_estimator = PCA(
        role=sagemaker_role_arn,
        num_components=1,
        instance_count=1,
        instance_type='ml.m5.large',
        )

    pca_estimator.feature_dim=500
    pca_estimator.subtract_mean=True,
    pca_estimator.algorithm_mode='randomized'
    pca_estimator.mini_batch_size=128
    
    return pca_estimator
    
@pytest.fixture(scope="module")
def inputs(pca_estimator):
    data_path = os.path.join(DATA_DIR, "one_p_mnist", "mnist.pkl.gz")
    pickle_args = {} if sys.version_info.major == 2 else {"encoding": "latin1"}

    # Load the data into memory as numpy arrays
    with gzip.open(data_path, "rb") as f:
        train_set, _, _ = pickle.load(f, **pickle_args)

    inputs = pca_estimator.record_set(train=train_set[0][:100])
    return inputs


def test_pca_estimator(sfn_client, sagemaker_session, sagemaker_role_arn, sfn_role_arn, pca_estimator, inputs):
    bucket_name = sagemaker_session.default_bucket()
    unique_name = '{}-{}'.format(BASE_NAME, datetime.now().strftime('%Y%m%d%H%M%S'))
    hyperparams = pca_estimator.hyperparameters()

    with timeout(minutes=DEFAULT_TIMEOUT_MINUTES):
        tp = TrainingPipeline(
            estimator=pca_estimator,
            role=sfn_role_arn,
            inputs=inputs,
            s3_bucket=bucket_name,
            pipeline_name = unique_name
        )
        tp.create()

        execution = tp.execute(job_name=unique_name, hyperparameters=hyperparams)
        out = execution.get_output(wait=True)
        assert out  # If fails, out is None.
        endpoint_arn = out['EndpointArn']

        workflow_execution_info = execution.describe()

        execution_arn = execution.execution_arn
        state_machine_definition = sfn_client.describe_state_machine_for_execution(executionArn=execution_arn)
        state_machine_definition['definition'] = json.loads(state_machine_definition['definition'])
        assert state_machine_definition['definition'] == tp.workflow.definition.to_dict()

        state_machine_arn = state_machine_definition['stateMachineArn']
        job_name = workflow_execution_info['name']
        s3_manifest_uri = inputs.s3_data
        status = 'SUCCEEDED'
        estimator_image_uri = retrieve(region=sagemaker_session.boto_region_name,  framework='pca')

        execution_info = sfn_client.describe_execution(executionArn=execution_arn)
        execution_info['input'] = json.loads(execution_info['input'])
        _=execution_info.pop('ResponseMetadata')
        _=execution_info.pop('output')

        s3_output_path = 's3://{bucket_name}/{workflow_name}/models'.format(bucket_name=bucket_name, workflow_name=unique_name)
        expected_execution_info = {'executionArn': execution_arn,
         'stateMachineArn': state_machine_arn,
         'inputDetails': {'included': True},
         'name': job_name,
         'outputDetails': {'included': True},
         'status': status,
         'startDate': execution_info['startDate'],
         'stopDate': execution_info['stopDate'],
         'inputDetails': {'included': True},
         'outputDetails': {'included': True},
         'input': {'Training': {'AlgorithmSpecification': {'TrainingImage': estimator_image_uri,
            'TrainingInputMode': 'File'},
           'OutputDataConfig': {'S3OutputPath': s3_output_path},
           'StoppingCondition': {'MaxRuntimeInSeconds': 86400},
           'ResourceConfig': {'InstanceCount': 1,
            'InstanceType': 'ml.m5.large',
            'VolumeSizeInGB': 30},
           'RoleArn': sagemaker_role_arn,
           'InputDataConfig': [{'DataSource': {'S3DataSource': {'S3DataDistributionType': 'ShardedByS3Key',
               'S3DataType': 'ManifestFile',
               'S3Uri': s3_manifest_uri}},
             'ChannelName': 'train'}],
           'HyperParameters': hyperparams,
           'TrainingJobName': 'estimator-' + job_name},
          'Create Model': {'ModelName': job_name,
           'PrimaryContainer': {'Image': estimator_image_uri,
            'Environment': {},
            'ModelDataUrl': 's3://' + bucket_name +'/' + unique_name + '/models/' + 'estimator-'+job_name + '/output/model.tar.gz'},
           'ExecutionRoleArn': sagemaker_role_arn},
          'Configure Endpoint': {'EndpointConfigName': job_name,
           'ProductionVariants': [{'ModelName': job_name,
             'InstanceType': 'ml.m5.large',
             'InitialInstanceCount': 1,
             'VariantName': 'AllTraffic'}]},
          'Deploy': {'EndpointName': job_name,
           'EndpointConfigName': job_name}}
        }
        assert execution_info == expected_execution_info
    
        # Cleanup
        state_machine_delete_wait(sfn_client, state_machine_arn)
        delete_sagemaker_endpoint(job_name, sagemaker_session)
        delete_sagemaker_endpoint_config(job_name, sagemaker_session)
        delete_sagemaker_model(job_name, sagemaker_session)
