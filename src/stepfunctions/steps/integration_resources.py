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
    RequestResponse = ""


def get_service_integration_arn(service, api, integration_pattern=IntegrationPattern.RequestResponse):

    """
    ARN builder for task integration
    Args:
        service (str): The service name for the service integration
        api (str): The api of the service integration
        integration_pattern (IntegrationPattern, optional): The integration pattern for the task. (Default: IntegrationPattern.RequestResponse)
    """
    arn = ""
    if integration_pattern == IntegrationPattern.RequestResponse:
        arn = f"arn:{get_aws_partition()}:states:::{service}:{api.value}"
    else:
        arn = f"arn:{get_aws_partition()}:states:::{service}:{api.value}.{integration_pattern.value}"
    return arn


