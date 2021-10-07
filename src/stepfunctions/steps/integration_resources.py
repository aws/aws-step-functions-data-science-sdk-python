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

import logging

from enum import Enum
from stepfunctions.steps.utils import get_aws_partition

logger = logging.getLogger('stepfunctions')


class IntegrationPattern(Enum):
    """
    Integration pattern enum classes for task integration resource arn builder
    """

    WaitForTaskToken = "waitForTaskToken"
    WaitForCompletion = "sync"
    RequestResponse = ""
    WaitForCompletionWithJsonResponse = "sync:2"


class ServiceIntegrationType(Enum):
    """
    Service Integration Types for service integration resources (see `Service Integration Patterns <https://docs.aws.amazon.com/step-functions/latest/dg/connect-to-resource.html`_ for more details.)
    """

    REQUEST_RESPONSE = "RequestResponse",
    RUN_JOB = "RunJob",
    WAIT_FOR_CALLBACK = "WaitForCallback"


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


def get_integration_pattern_from_service_integration_type(service_integration_type):
    """
    Returns the integration pattern to use for the service integration type.
    IntegrationPattern.RequestResponse is returned by default if the service type is not recognized
    Args:
        service_integration_type(ServiceIntegrationType): Service integration type to use to get the integration pattern
    """

    if service_integration_type == ServiceIntegrationType.RUN_JOB:
        return IntegrationPattern.WaitForCompletion
    elif service_integration_type == ServiceIntegrationType.WAIT_FOR_CALLBACK:
        return IntegrationPattern.WaitForTaskToken
    else:
        if not isinstance(service_integration_type, ServiceIntegrationType):
            logger.warning(f"Invalid Service integration type ({service_integration_type}) - returning IntegrationPattern.RequestResponse by default")
        return IntegrationPattern.RequestResponse


def is_integration_type_valid(service_integration_type, supported_integration_types):
    if not isinstance(service_integration_type, ServiceIntegrationType):
        raise ValueError(f"Invalid type used for service_integration_type arg ({service_integration_type}, "
                         f"{type(service_integration_type)}). Accepted type: {ServiceIntegrationType}")
    elif service_integration_type not in supported_integration_types:
        raise ValueError(f"Service Integration Type ({service_integration_type.name}) is not supported for this step - "
                         f"Please use one of the following: "
                         f"{[integ_type.name for integ_type in supported_integration_types]}")
