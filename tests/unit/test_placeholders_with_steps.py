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

from stepfunctions.steps import Pass, Succeed, Fail, Wait, Choice, ChoiceRule, Parallel, Map, Task, Retry, Catch, Chain, Graph
from stepfunctions.inputs import ExecutionInput, StepInput

def test_workflow_input_placeholder():

    workflow_input = ExecutionInput()
    test_step = Pass(
        state_id='StateOne', 
        parameters={
            'ParamA': 'SampleValueA',
            'ParamB': workflow_input,
            'ParamC': workflow_input['Key01'],
            'ParamD': workflow_input['Key02']['Key03'],
            'ParamE': workflow_input['Key01']['Key03'],
        }
    )

    expected_repr = {
        "Type": "Pass",
        "Parameters": {
            "ParamA": "SampleValueA",
            "ParamB.$": "$$.Execution.Input",
            "ParamC.$": "$$.Execution.Input['Key01']",
            "ParamD.$": "$$.Execution.Input['Key02']['Key03']",
            "ParamE.$": "$$.Execution.Input['Key01']['Key03']"
        },
        "End": True
    }

    assert test_step.to_dict() == expected_repr

def test_step_input_placeholder():

    test_step_01 = Pass(
        state_id='StateOne'
    )

    test_step_02 = Pass(
        state_id='StateTwo',
        parameters={
            'ParamA': test_step_01.output(),
            'ParamB': test_step_01.output()["Response"]["Key02"],
            "ParamC": "SampleValueC"
        }
    )

    expected_repr = {
        "Type": "Pass",
        "Parameters": {
            "ParamA.$": "$",
            "ParamB.$": "$['Response']['Key02']",
            "ParamC": "SampleValueC"
        },
        "End": True
    }

    assert test_step_02.to_dict() == expected_repr

    
def test_workflow_with_placeholders():
    workflow_input = ExecutionInput()

    test_step_01 = Pass(
        state_id='StateOne',
        parameters={
            'ParamA': workflow_input['Key02']['Key03'],
            'ParamD': workflow_input['Key01']['Key03'],
        }
    )

    test_step_02 = Pass(
        state_id='StateTwo',
        parameters={
            'ParamC': workflow_input["Key05"],
            "ParamB": "SampleValueB",
            "ParamE": test_step_01.output()["Response"]["Key04"]
        }
    )

    test_step_03 = Pass(
        state_id='StateThree',
        parameters={
            'ParamG': "SampleValueG",
            "ParamF": workflow_input["Key06"],
            "ParamH": "SampleValueH"
        }
    )

    workflow_definition = Chain([test_step_01, test_step_02, test_step_03])

    result = Graph(workflow_definition).to_dict()

    expected_workflow_repr = {
        "StartAt": "StateOne",
        "States": {
            "StateOne": {
                "Type": "Pass",
                "Parameters": {
                    "ParamA.$": "$$.Execution.Input['Key02']['Key03']",
                    "ParamD.$": "$$.Execution.Input['Key01']['Key03']"
                },
                "Next": "StateTwo"
            },
            "StateTwo": {
                "Type": "Pass",
                "Parameters": {
                    "ParamC.$": "$$.Execution.Input['Key05']",
                    "ParamB": "SampleValueB",
                    "ParamE.$": "$['Response']['Key04']"
                },
                "Next": "StateThree"
            },
            "StateThree": {
                "Type": "Pass",
                "Parameters": {
                    "ParamG": "SampleValueG",
                    "ParamF.$": "$$.Execution.Input['Key06']",
                    "ParamH": "SampleValueH"
                },
                "End": True
            }
        }
    }

    assert result == expected_workflow_repr
 
def test_step_input_order_validation():
    workflow_input = ExecutionInput()

    test_step_01 = Pass(
        state_id='StateOne',
        parameters={
            'ParamA': workflow_input['Key02']['Key03'],
            'ParamD': workflow_input['Key01']['Key03'],
        }
    )

    test_step_02 = Pass(
        state_id='StateTwo',
        parameters={
            'ParamC': workflow_input["Key05"],
            "ParamB": "SampleValueB",
            "ParamE": test_step_01.output()["Response"]["Key04"]
        }
    )

    test_step_03 = Pass(
        state_id='StateThree',
        parameters={
            'ParamG': "SampleValueG",
            "ParamF": workflow_input["Key06"],
            "ParamH": "SampleValueH"
        }
    )

    workflow_definition = Chain([test_step_01, test_step_03, test_step_02])

    with pytest.raises(ValueError):
        result = Graph(workflow_definition).to_dict()

def test_map_state_with_placeholders():
    workflow_input = ExecutionInput()

    map_state = Map('MapState01')
    iterator_state = Pass(
        'TrainIterator',
        parameters={
            'ParamA': map_state.output()['X']["Y"],
            'ParamB': workflow_input["Key01"]["Key02"]["Key03"]
    })

    map_state.attach_iterator(iterator_state)
    workflow_definition = Chain([map_state])

    expected_repr = {
        "StartAt": "MapState01",
        "States": {
            "MapState01": {
                "Type": "Map",
                "End": True,
                "Iterator": {
                    "StartAt": "TrainIterator",
                    "States": {
                        "TrainIterator": {
                            "Parameters": {
                                "ParamA.$": "$['X']['Y']",
                                "ParamB.$": "$$.Execution.Input['Key01']['Key02']['Key03']"
                            },
                            "Type": "Pass",
                            "End": True
                        }
                    }
                }
            }
        }
    }

    result = Graph(workflow_definition).to_dict()
    assert result == expected_repr

def test_parallel_state_with_placeholders():
    workflow_input = ExecutionInput()

    parallel_state = Parallel('ParallelState01')
    
    branch_A = Pass(
        'Branch_A',
        parameters={
            'ParamA': parallel_state.output()['A']["B"],
            'ParamB': workflow_input["Key01"]
    })

    branch_B = Pass(
        'Branch_B',
        parameters={
            'ParamA': "TestValue",
            'ParamB': parallel_state.output()["Response"]["Key"]["State"]
    })

    branch_C = Pass(
        'Branch_C',
        parameters={
            'ParamA': parallel_state.output()['A']["B"].get("C", float),
            'ParamB': "HelloWorld"
    })

    parallel_state.add_branch(branch_A)
    parallel_state.add_branch(branch_B)
    parallel_state.add_branch(branch_C)

    workflow_definition = Chain([parallel_state])
    result = Graph(workflow_definition).to_dict()

    expected_repr = {
        "StartAt": "ParallelState01",
        "States": {
            "ParallelState01": {
                "Type": "Parallel",
                "End": True,
                "Branches": [
                    {
                        "StartAt": "Branch_A",
                        "States": {
                            "Branch_A": {
                                "Parameters": {
                                    "ParamA.$": "$['A']['B']",
                                    "ParamB.$": "$$.Execution.Input['Key01']"
                                },
                                "Type": "Pass",
                                "End": True
                            }
                        }
                    },
                    {
                        "StartAt": "Branch_B",
                        "States": {
                            "Branch_B": {
                                "Parameters": {
                                    "ParamA": "TestValue",
                                    "ParamB.$": "$['Response']['Key']['State']"
                                },
                                "Type": "Pass",
                                "End": True
                            }
                        }
                    },
                    {
                        "StartAt": "Branch_C",
                        "States": {
                            "Branch_C": {
                                "Parameters": {
                                    "ParamA.$": "$['A']['B']['C']",
                                    "ParamB": "HelloWorld"
                                },
                                "Type": "Pass",
                                "End": True
                            }
                        }
                    }
                ]
            }
        }
    }

    assert result == expected_repr


def test_choice_state_with_placeholders():

    first_state = Task('FirstState', resource='arn:aws:lambda:us-east-1:1234567890:function:FirstState')
    retry = Chain([Pass('Retry'), Pass('Cleanup'), first_state])

    choice_state = Choice('Is Completed?')
    choice_state.add_choice(
        ChoiceRule.BooleanEquals(choice_state.output()["Completed"], True), 
        Succeed('Complete')
    )
    choice_state.add_choice(
        ChoiceRule.BooleanEquals(choice_state.output()["Completed"], False), 
        retry
    )

    first_state.next(choice_state)

    result = Graph(first_state).to_dict()

    expected_repr = {
        "StartAt": "FirstState",
        "States": {
            "FirstState": {
                "Resource": "arn:aws:lambda:us-east-1:1234567890:function:FirstState",
                "Type": "Task",
                "Next": "Is Completed?"
            },
            "Is Completed?": {
                "Type": "Choice",
                "Choices": [
                    {
                        "Variable": "$['Completed']",
                        "BooleanEquals": True,
                        "Next": "Complete"
                    },
                    {
                        "Variable": "$['Completed']",
                        "BooleanEquals": False,
                        "Next": "Retry"
                    }
                ]
            },
            "Complete": {
                "Type": "Succeed"
            },
            "Retry": {
                "Type": "Pass",
                "Next": "Cleanup"
            },
            "Cleanup": {
                "Type": "Pass",
                "Next": "FirstState"
            }
        }
    }

    assert result == expected_repr

def test_schema_validation_for_step_input():
    
    test_step_01 = Pass(
        state_id='StateOne',
        output_schema={
            "Response": {
                "Key01": str
            }
        }
    )

    with pytest.raises(ValueError):
        test_step_02 = Pass(
            state_id='StateTwo',
            parameters={
                'ParamA': test_step_01.output()["Response"]["Key02"],
                "ParamB": "SampleValueB"
            }
        )
    
    with pytest.raises(ValueError):
        test_step_03 = Pass(
            state_id='StateTwo',
            parameters={
                'ParamA': test_step_01.output()["Response"].get("Key01", float),
                "ParamB": "SampleValueB"
            }
        )
