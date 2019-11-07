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
from stepfunctions.workflow.widgets import EventsTableWidget
PASS_WORKFLOW_EVENTS = [
    {
        'timestamp': datetime(2019, 9, 1, 13, 45, 47, 940000),
        'type': 'ExecutionStarted',
        'id': 1,
        'previousEventId': 0,
        'executionStartedEventDetails': {
            'input': '{}',
            'roleArn': 'arn:aws:iam::099764291644:role/stepfunctions'
        }
    },
    {
        'timestamp': datetime(2019, 9, 1, 13, 46, 50, 215000),
        'type': 'PassStateEntered',
        'id': 2,
        'previousEventId': 0,
        'stateEnteredEventDetails': {
            'name': 'HelloWorld1234',
            'input': '{}'
        }
    },
    {
        'timestamp': datetime(2019, 9, 1, 13, 47, 9, 396000),
        'type': 'PassStateExited',
        'id': 3,
        'previousEventId': 2,
        'stateExitedEventDetails': {
            'name': 'HelloWorld1234',
            'output': '"Hello World!"'
        }
    },
    {
        'timestamp': datetime(2019, 9, 1, 13, 47, 24, 724000),
        'type': 'ExecutionSucceeded',
        'id': 4,
        'previousEventId': 3,
        'executionSucceededEventDetails': {
            'output': '"Hello World!"'
        }
    }
]
LAMBDA_STATE_NAME = "Lambda Name"
LAMBDA_RESOURCE_NAME = "Lambda"
LAMBDA_WORKFLOW_EVENTS = [
    {
        'timestamp': datetime(2019, 9, 1, 13, 54, 21, 366000),
        'type': 'ExecutionStarted',
        'id': 1,
        'previousEventId': 0,
        'executionStartedEventDetails': {
            'input': '{}',
            'roleArn': 'arn:aws:iam::012345678901:role/stepfunctions'
        }
    },
    {
        'timestamp': datetime(2019, 9, 1, 13, 55, 30, 169000),
        'type': 'TaskStateEntered',
        'id': 2,
        'previousEventId': 1,
        'stateEnteredEventDetails': {
            'name': LAMBDA_STATE_NAME,
            'input': '"Hello World!"'
        }
    },
    {
        'timestamp': datetime(2019, 9, 1, 13, 55, 30, 169000),
        'type': 'LambdaFunctionScheduled',
        'id': 3,
        'previousEventId': 2,
        'lambdaFunctionScheduledEventDetails': {
            'resource': 'arn:aws:lambda:us-east-1:012345678901:function:serverlessrepo-sample-lambda-helloworld-V3LUDGZAC5KB',
            'input': '"Hello World!"'
        }
    },
    {
        'timestamp': datetime(2019, 9, 1, 13, 55, 30, 192000),
        'type': 'LambdaFunctionStarted',
        'id': 4,
        'previousEventId': 3
    },
    {
        'timestamp': datetime(2019, 9, 1, 13, 55, 30, 241000),
        'type': 'LambdaFunctionSucceeded',
        'id': 5,
        'previousEventId': 4,
        'lambdaFunctionSucceededEventDetails': {
            'output': 'null'
        }
    },
    {
        'timestamp': datetime(2019, 9, 1, 13, 55, 30, 241000),
        'type': 'TaskStateExited',
        'id': 6,
        'previousEventId': 5,
        'stateExitedEventDetails': {
            'name': LAMBDA_STATE_NAME,
            'output': 'null'
        }
    },
    {
        'timestamp': datetime(2019, 9, 1, 13, 55, 30, 241000),
        'type': 'ExecutionSucceeded',
        'id': 7,
        'previousEventId': 6,
        'executionSucceededEventDetails': {
            'output': 'null'
        }
    }
]


def test_empty_events_table():
    widget = EventsTableWidget([])
    html_snippet = widget.show()
    assert '<td class="awsui-table-row">' not in html_snippet
    assert '<table class="table-widget">' in html_snippet


def test_events_table():
    widget = EventsTableWidget(PASS_WORKFLOW_EVENTS)
    html_snippet = widget.show()
    assert html_snippet.count(
        '<tr class="awsui-table-row">') == len(PASS_WORKFLOW_EVENTS)


def test_lambda_workflow_events_table():
    widget = EventsTableWidget(LAMBDA_WORKFLOW_EVENTS)
    html_snippet = widget.show()
    assert html_snippet.count(
        '<tr class="awsui-table-row">') == len(LAMBDA_WORKFLOW_EVENTS)
    assert html_snippet.count('<td>{}</td>'.format(LAMBDA_STATE_NAME)) == 5
    assert html_snippet.count(
        """<td><a class='disabled' target="_blank">{}</a></td>""".format(LAMBDA_RESOURCE_NAME)) == 3