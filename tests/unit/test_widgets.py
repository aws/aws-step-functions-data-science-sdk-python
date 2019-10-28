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
import json

from stepfunctions.steps import *
from stepfunctions.workflow.widgets import WorkflowGraphWidget, ExecutionGraphWidget


REGION = 'test-region'
WORKFLOW = 'HelloWorld'
EXECUTION_ARN = 'arn:aws:states:{region}:1234567890:execution:{workflow}:execution-1'.format(region=REGION,
                                                                                             workflow=WORKFLOW)


def test_workflow_graph():
    graph = Graph(Chain([Pass('Prepare Data'), Pass('Start Training'), Pass('Batch Transform'), Pass('Deploy')]))

    widget = WorkflowGraphWidget(graph.to_json())
    html_snippet = widget.show(portrait=False)

    assert "layout: 'LR'" in html_snippet.data
    assert 'var graph = new sfn.StateMachineGraph(definition, elementId, options);' in html_snippet.data

    html_snippet = widget.show(portrait=True)
    assert "layout: 'TB'" in html_snippet.data


def test_execution_graph():
    graph = Graph(Chain([Pass('Prepare Data'), Pass('Start Training'), Pass('Batch Transform'), Pass('Deploy')]))
    events = [{}, {}, {}]

    widget = ExecutionGraphWidget(graph.to_json(), json.dumps(events), EXECUTION_ARN)
    html_snippet = widget.show()
    assert 'var graph = new sfn.StateMachineExecutionGraph(definition, events, elementId, options);' in html_snippet.data
    
    expected_aws_sfn_executions_detail_url='<a href="https://console.aws.amazon.com/states/home?region={region}#/executions/details/{execution_arn}" target="_blank"> Inspect in AWS Step Functions </a>'
    assert expected_aws_sfn_executions_detail_url.format(region=REGION,
                                                         execution_arn=EXECUTION_ARN) in html_snippet.data
