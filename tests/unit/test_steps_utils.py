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

import boto3
import logging
import pytest

from enum import Enum
from unittest.mock import patch

from stepfunctions.steps.utils import get_aws_partition, merge_dicts
from stepfunctions.steps.integration_resources import IntegrationPattern,\
    get_service_integration_arn, is_integration_pattern_valid


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
    d1 = {
        'a': {
            'aa': 1,
            'bb': 2,
            'cc': 3
        },
        'b': 1
    }

    d2 = {
        'a': {
            'bb': {
                'aaa': 1,
                'bbb': 2
            }
        },
        'b': 2,
        'c': 3
    }

    merge_dicts(d1, d2)
    assert d1 == {
        'a': {
            'aa': 1,
            'bb': {
                'aaa': 1,
                'bbb': 2
            },
            'cc': 3
        },
        'b': 2,
        'c': 3
    }


@pytest.mark.parametrize("service_integration_type", [
    None,
    "IntegrationPatternStr",
    0
])
def test_is_integration_pattern_valid_with_invalid_type_raises_type_error(service_integration_type):
    with pytest.raises(TypeError):
        is_integration_pattern_valid(service_integration_type, [IntegrationPattern.WaitForTaskToken])


def test_is_integration_pattern_valid_with_non_supported_type_raises_value_error():
    with pytest.raises(ValueError):
        is_integration_pattern_valid(IntegrationPattern.WaitForTaskToken, [IntegrationPattern.WaitForCompletion])
