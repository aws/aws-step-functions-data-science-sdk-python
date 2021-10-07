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
from stepfunctions.steps.integration_resources import IntegrationPattern, ServiceIntegrationType,\
    get_integration_pattern_from_service_integration_type, get_service_integration_arn, is_integration_type_valid


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


@pytest.mark.parametrize("service_integration_type, expected_integration_pattern", [
    (ServiceIntegrationType.REQUEST_RESPONSE, IntegrationPattern.RequestResponse),
    (ServiceIntegrationType.RUN_JOB, IntegrationPattern.WaitForCompletion),
    (ServiceIntegrationType.WAIT_FOR_CALLBACK, IntegrationPattern.WaitForTaskToken)
])
@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_get_integration_pattern_from_service_integration_type(service_integration_type, expected_integration_pattern):
    integration_pattern = get_integration_pattern_from_service_integration_type(service_integration_type)
    assert integration_pattern == expected_integration_pattern


@pytest.mark.parametrize("service_integration_type", [
    None,
    "ServiceIntegrationTypeStr",
    IntegrationPattern.RequestResponse
])
@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_get_integration_pattern_from_service_integration_type_with_invalid_type(service_integration_type, caplog):
    with caplog.at_level(logging.WARNING):
        integration_pattern = get_integration_pattern_from_service_integration_type(service_integration_type)
        assert 'WARNING' in caplog.text
    assert integration_pattern == IntegrationPattern.RequestResponse


@pytest.mark.parametrize("service_integration_type", [
    None,
    "ServiceIntegrationTypeStr",
    IntegrationPattern.RequestResponse
])
def test_is_integration_type_valid_with_invalid_type_raises_value_error(service_integration_type):
    with pytest.raises(ValueError):
        is_integration_type_valid(service_integration_type, [ServiceIntegrationType.REQUEST_RESPONSE])


def test_is_integration_type_valid_with_non_supported_type_raises_value_error():
    with pytest.raises(ValueError):
        is_integration_type_valid(ServiceIntegrationType.WAIT_FOR_CALLBACK, [ServiceIntegrationType.REQUEST_RESPONSE])
