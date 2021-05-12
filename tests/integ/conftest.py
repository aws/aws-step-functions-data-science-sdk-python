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
import boto3
import gzip
import sys
import os
import pickle
from sagemaker import Session
from sagemaker.amazon import pca
from sagemaker.sklearn.processing import SKLearnProcessor
from stepfunctions.steps.utils import get_aws_partition
from tests.integ import DATA_DIR

@pytest.fixture(scope="session")
def sfn_client():
    return boto3.client('stepfunctions')

@pytest.fixture(scope="session")
def sagemaker_client():
    return boto3.client('sagemaker')

@pytest.fixture(scope="session")
def sagemaker_session():
    sess = Session()
    return sess

@pytest.fixture(scope="session")
def aws_account_id():
    account_id = boto3.client("sts").get_caller_identity().get("Account")
    return account_id

@pytest.fixture(scope="session")
def sfn_role_arn(aws_account_id):
    return f"arn:{get_aws_partition()}:iam::{aws_account_id}:role/StepFunctionsMLWorkflowExecutionFullAccess"

@pytest.fixture(scope="session")
def sagemaker_role_arn(aws_account_id):
    return f"arn:{get_aws_partition()}:iam::{aws_account_id}:role/SageMakerRole"

@pytest.fixture(scope="session")
def pca_estimator_fixture(sagemaker_role_arn):
    estimator = pca.PCA(
        role=sagemaker_role_arn,
        instance_count=1,
        instance_type="ml.m5.large",
        num_components=48
    )
    return estimator

@pytest.fixture(scope="session")
def sklearn_processor_fixture(sagemaker_role_arn):
    processor = SKLearnProcessor(
        framework_version="0.20.0",
        role=sagemaker_role_arn,
        instance_type="ml.m5.xlarge",
        instance_count=1,
        max_runtime_in_seconds=300
    )
    return processor

@pytest.fixture(scope="session")
def train_set():
    data_path = os.path.join(DATA_DIR, "one_p_mnist", "mnist.pkl.gz")
    pickle_args = {} if sys.version_info.major == 2 else {"encoding": "latin1"}

    # Load the data into memory as numpy arrays
    with gzip.open(data_path, "rb") as f:
        train_set, _, _ = pickle.load(f, **pickle_args)

    return train_set

@pytest.fixture(scope="session")
def record_set_fixture(pca_estimator_fixture, train_set):
    record_set = pca_estimator_fixture.record_set(train=train_set[0][:100])
    return record_set