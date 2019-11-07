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

import boto3
import sys
import time

from datetime import datetime

AWS_SAGEMAKER_URL = "https://console.aws.amazon.com/sagemaker/home?region={region}#/{resource_type}/{resource}"
AWS_SFN_EXECUTIONS_DETAIL_URL = "https://console.aws.amazon.com/states/home?region={region}#/executions/details/{execution_arn}"
AWS_SFN_STATE_MACHINE_URL = "https://console.aws.amazon.com/states/home?region={region}#/statemachines/view/{state_machine_arn}"

AWS_TABLE_CSS = """
    .table-widget {
        width: 100%;
        font-size: 14px;
        line-height: 28px;
        color: #545b64;
        border-spacing: 0;
        background-color: #fff;
        border-color: grey;
        background: #fafafa;
    }

    .table-widget thead th {
        text-align: left !important;
        color: #879596;
        padding: 0.3em 2em;
        border-bottom: 1px solid #eaeded;
        min-height: 4rem;
        line-height: 28px;
    }

    .table-widget thead th:first-of-type {
    }

    .table-widget td {
        overflow-wrap: break-word;
        padding: 0.4em 2em;
        line-height: 28px;
        text-align: left !important;
        background: #fff;
        border-bottom: 1px solid #eaeded;
        border-top: 1px solid transparent;
    }

    .table-widget td:before {
        content: "";
        height: 3rem;
    }

    a {
        cursor: pointer;
        text-decoration: none !important;
        color: #007dbc;
    }

    a:hover {
        text-decoration: underline !important;
    }

    a.disabled {
        color: black;
        cursor: default;
        pointer-events: none;
    }

    .hide {
        display: none;
    }

    pre {
        white-space: pre-wrap;
    }
"""

def format_time(timestamp):
    if timestamp is None:
        return "-"
    time = timestamp.strftime("%b %d, %Y %I:%M:%S.%f")[:-3]
    return time + timestamp.strftime(" %p")

def get_timestamp(date):
    if sys.version_info[0] < 3 or sys.version_info[1] < 4:
        # python version < 3.3
        return time.mktime(date.timetuple())
    else:
        return date.timestamp()

def get_elapsed_ms(start_datetime, end_datetime):
    elapsed_time_seconds = (end_datetime - start_datetime).microseconds
    return elapsed_time_seconds / 1000

def create_sfn_execution_url(execution_arn):
    arn_segments = execution_arn.split(":")
    region_name = arn_segments[3]
    return AWS_SFN_EXECUTIONS_DETAIL_URL.format(region=region_name, execution_arn=execution_arn)

def create_sfn_workflow_url(state_machine_arn):
    arn_segments = state_machine_arn.split(":")
    region_name = arn_segments[3]
    return AWS_SFN_STATE_MACHINE_URL.format(region=region_name, state_machine_arn=state_machine_arn)

def sagemaker_console_link(resource_type, resource):
    region_name = boto3.session.Session().region_name
    return AWS_SAGEMAKER_URL.format(region=region_name, resource_type=resource_type, resource=resource)
     
