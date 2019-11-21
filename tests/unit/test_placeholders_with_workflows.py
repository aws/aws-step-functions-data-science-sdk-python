# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.

# Licensed under the Apache License, Version 2.0 (the "License").
# You may not use this file except in compliance with the License.
# A copy of the License is located at

#     http://www.apache.org/licenses/LICENSE-2.0

# or in the "license" file accompanying this file. This file is distributed 
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either 
# express or implied. See the License for the specific language governing 
# permissions and limitations under the License.
from __future__ import absolute_import

import pytest
from mock import MagicMock

from datetime import datetime

from stepfunctions.inputs import ExecutionInput, StepInput
from stepfunctions.steps import Pass, Chain
from stepfunctions.workflow import Workflow

@pytest.fixture(scope="module")
def client():
    mock = MagicMock()
    return mock

@pytest.fixture(scope="module")
def workflow(client):
    execution_input = ExecutionInput()

    test_step_01 = Pass(
        state_id='StateOne',
        parameters={
            'ParamA': execution_input['Key02']['Key03'],
            'ParamD': execution_input['Key01']['Key03'],
        }
    )

    test_step_02 = Pass(
        state_id='StateTwo',
        parameters={
            'ParamC': execution_input["Key05"],
            "ParamB": "SampleValueB",
            "ParamE": test_step_01.output()["Response"]["Key04"]
        }
    )

    test_step_03 = Pass(
        state_id='StateThree',
        parameters={
            'ParamG': "SampleValueG",
            "ParamF": execution_input["Key06"],
            "ParamH": "SampleValueH",
            "ParamI": test_step_02.output()
        }
    )

    workflow_definition = Chain([test_step_01, test_step_02, test_step_03])
    workflow = Workflow(
        name='TestWorkflow',
        definition=workflow_definition,
        role='testRoleArn',
        execution_input=execution_input,
        client=client
    )
    return workflow


def test_workflow_execute_with_invalid_input(workflow):
    
    with pytest.raises(ValueError):
        workflow.execute(inputs={})

    with pytest.raises(ValueError):
        workflow.execute(inputs={
            "Key02": {
                "Key03": "Hello"
            }, 
            "Key01": {
                "Key03": "World"
            }, 
            "Key05": "Test", 
            "Key06": 123
        })

def test_workflow_execute_with_valid_input(client, workflow):

    workflow.create()
    execution = workflow.execute(inputs={
        "Key02": {
            "Key03": "Hello"
        }, 
        "Key01": {
            "Key03": "World"
        }, 
        "Key05": "Test01", 
        "Key06": "Test02"
    })

    client.create_state_machine.assert_called()
    client.start_execution.assert_called()
