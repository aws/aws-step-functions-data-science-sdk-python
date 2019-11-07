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

from stepfunctions.workflow.widgets import ExecutionsTableWidget
from stepfunctions.workflow import Execution

REGION = 'us-east-1'
WORKFLOW_NAME = 'HelloWorld'
STATUS = 'RUNNING'

@pytest.fixture
def executions():
    workflow = MagicMock()
    workflow.state_machine_arn = 'arn:aws:states:{}:1234567890:stateMachine:{}'.format(REGION, WORKFLOW_NAME)
    execution_arn = 'arn:aws:states:{}:1234567890:execution:{}:execution-1'.format(REGION, WORKFLOW_NAME)

    executions = [
        Execution(
            name=WORKFLOW_NAME,
            workflow=workflow,
            execution_arn=execution_arn,
            start_date=datetime.now(),
            stop_date=None,
            status=STATUS,
            client=None
        )
    ]
    return executions

def test_empty_executions_table():
    widget = ExecutionsTableWidget([])
    html_snippet = widget.show()
    assert '<tr class="awsui-table-row">' not in html_snippet
    assert '<table class="table-widget">' in html_snippet

def test_executions_table(executions):
    widget = ExecutionsTableWidget(executions)
    html_snippet = widget.show()
    assert html_snippet.count('<tr class="awsui-table-row">') == len(executions)
    assert WORKFLOW_NAME in html_snippet
    assert STATUS in html_snippet
