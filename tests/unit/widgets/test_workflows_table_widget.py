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

from unittest.mock import MagicMock
from datetime import datetime

from stepfunctions.workflow.widgets import WorkflowsTableWidget


WORKFLOW_NAME = 'HelloWorld'
STATE_MACHINE_ARN = 'arn:aws:states:us-east-1:1234567890:stateMachine:HelloWorld'


@pytest.fixture
def workflows():
    return [
        {
            'stateMachineArn': STATE_MACHINE_ARN,
            'name': WORKFLOW_NAME,
            'creationDate': datetime(2019, 1, 1)
        }
    ]

def test_empty_workflows_table():
    widget = WorkflowsTableWidget([])
    html_snippet = widget.show()
    assert '<tr class="awsui-table-row">' not in html_snippet
    assert '<table class="table-widget">' in html_snippet

def test_workflows_table(workflows):
    widget = WorkflowsTableWidget(workflows)
    html_snippet = widget.show()
    assert html_snippet.count('<tr class="awsui-table-row">') == len(workflows)
    assert WORKFLOW_NAME in html_snippet
    assert STATE_MACHINE_ARN in html_snippet
