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

# Test if boto3 session can fetch correct aws partition info from test environment

from stepfunctions.steps.utils import get_aws_partition, merge_dicts
from stepfunctions.steps.integration_resources import IntegrationPattern, get_service_integration_arn
import boto3
from unittest.mock import patch
from enum import Enum


testService = "sagemaker"


class TestApi(Enum):
    CreateTrainingJob = "createTrainingJob"


@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_util_get_aws_partition_aws():
    cur_partition = get_aws_partition()
    assert cur_partition == "aws"


@patch.object(boto3.session.Session, 'region_name', 'cn-north-1')
def test_util_get_aws_partition_aws_cn():
    cur_partition = get_aws_partition()
    assert cur_partition == "aws-cn"


@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_arn_builder_sagemaker_no_wait():
    arn = get_service_integration_arn(testService, TestApi.CreateTrainingJob)
    assert arn == "arn:aws:states:::sagemaker:createTrainingJob"


@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_arn_builder_sagemaker_wait_completion():
    arn = get_service_integration_arn(testService, TestApi.CreateTrainingJob,
                                      IntegrationPattern.WaitForCompletion)
    assert arn == "arn:aws:states:::sagemaker:createTrainingJob.sync"


def test_merge_dicts():
    d1 = {'a': {'aa': 1, 'bb': 2, 'cc': 3}, 'b': 1}
    d2 = {'a': {'bb': {'aaa': 1, 'bbb': 2}}, 'b': 2, 'c': 3}

    merge_dicts(d1, d2, 'd1', 'd2')
    assert d1 == {'a': {'aa': 1, 'bb': {'aaa': 1, 'bbb': 2}, 'cc': 3}, 'b': 2, 'c': 3}
