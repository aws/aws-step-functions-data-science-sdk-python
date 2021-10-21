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

from enum import Enum
from stepfunctions.steps.utils import get_aws_partition


class IntegrationPattern(Enum):
    """
    Integration pattern enum classes for task integration resource arn builder
    """

    WaitForTaskToken = "waitForTaskToken"
    WaitForCompletion = "sync"
    CallAndContinue = ""


def get_service_integration_arn(service, api, integration_pattern=IntegrationPattern.CallAndContinue, version=None):

    """
    ARN builder for task integration
    Args:
        service (str): The service name for the service integration
        api (str): The api of the service integration
        integration_pattern (IntegrationPattern, optional): The integration pattern for the task. (Default: IntegrationPattern.CallAndContinue)
        version (int, optional): The version of the resource to use. (Default: None)
    """
    arn = ""
    if integration_pattern == IntegrationPattern.CallAndContinue:
        arn = f"arn:{get_aws_partition()}:states:::{service}:{api.value}"
    else:
        arn = f"arn:{get_aws_partition()}:states:::{service}:{api.value}.{integration_pattern.value}"

    if version:
        arn = f"{arn}:{str(version)}"

    return arn


def is_integration_pattern_valid(integration_pattern, supported_integration_patterns):
    if not isinstance(integration_pattern, IntegrationPattern):
        raise TypeError(f"Integration pattern must be of type {IntegrationPattern}")
    elif integration_pattern not in supported_integration_patterns:
        raise ValueError(f"Integration Pattern ({integration_pattern.name}) is not supported for this step - "
                         f"Please use one of the following: "
                         f"{[integ_type.name for integ_type in supported_integration_patterns]}")
