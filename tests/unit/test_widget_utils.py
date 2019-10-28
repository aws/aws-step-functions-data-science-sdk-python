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

from datetime import datetime

from stepfunctions.workflow import Execution
from stepfunctions.workflow.widgets.utils import (
    AWS_SFN_EXECUTIONS_DETAIL_URL,
    format_time,
    get_elapsed_ms,
    create_sfn_execution_url
)

REGION = 'us-east-1'
WORKFLOW_NAME = 'HelloWorld'
STATUS = 'RUNNING'

EXECUTION_ARN = 'arn:aws:states:{}:1234567890:execution:{}:execution-1'.format(REGION, WORKFLOW_NAME)
expected_aws_sfn_executions_detail_url = "https://console.aws.amazon.com/states/home?region={region}#/executions/details/{execution_arn}"


def test_sfn_console_url():
    assert AWS_SFN_EXECUTIONS_DETAIL_URL == expected_aws_sfn_executions_detail_url

def test_format_time():
    none_time = format_time(None)
    formatted_time = format_time(datetime(2020, 1, 2, 13, 30, 45, 123000))

    assert none_time == "-"
    assert formatted_time == 'Jan 02, 2020 01:30:45.123 PM'

def test_get_elapsed_ms():
    elapsed_time_microseconds = 10000
    start_time = datetime(2020, 1, 2, 13, 30, 45, 123000)
    end_time = datetime(2020, 1, 2, 13, 30, 45, 123000 +
                        elapsed_time_microseconds)
    calculated_elapsed_milliseconds = get_elapsed_ms(start_time, end_time)

    assert calculated_elapsed_milliseconds == elapsed_time_microseconds / 1000

def test_create_sfn_execution_url():
    sfn_execution_url = create_sfn_execution_url(EXECUTION_ARN)
    assert sfn_execution_url == expected_aws_sfn_executions_detail_url.format(
        region=REGION, execution_arn=EXECUTION_ARN)
