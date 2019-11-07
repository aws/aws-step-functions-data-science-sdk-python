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

from stepfunctions.inputs import ExecutionInput, StepInput

def test_placeholder_creation_with_subscript_operator():
    step_input = StepInput()
    placeholder_variable = step_input["A"]
    assert placeholder_variable.name == "A"
    assert placeholder_variable.type is None

def test_placeholder_creation_with_type():
    workflow_input = ExecutionInput()
    placeholder_variable = workflow_input["A"]["b"].get("C", float)
    assert placeholder_variable.name == "C"
    assert placeholder_variable.type == float

def test_placeholder_creation_with_int_key():
    workflow_input = ExecutionInput()
    placeholder_variable = workflow_input["A"][0]
    assert placeholder_variable.name == 0
    assert placeholder_variable.type == None

def test_placeholder_creation_with_invalid_key():
    step_input = StepInput()
    with pytest.raises(ValueError):
        step_input["A"][1.3]
    with pytest.raises(ValueError):
        step_input["A"].get(1.2, str)

def test_placeholder_creation_failure_with_type():
    workflow_input = ExecutionInput()
    placeholder_variable = workflow_input["A"]["b"].get("C", float)
    with pytest.raises(ValueError):
        workflow_input["A"]["b"].get("C", int)

def test_placeholder_path():
    workflow_input = ExecutionInput()
    placeholder_variable = workflow_input["A"]["b"]["C"]
    expected_path = ["A", "b", "C"]
    assert placeholder_variable._get_path() == expected_path

def test_placeholder_contains():
    step_input = StepInput()
    var_one = step_input["Key01"]
    var_two = step_input["Key02"]["Key03"]
    var_three = step_input["Key01"]["Key04"]
    var_four = step_input["Key05"]

    step_input_two = StepInput()
    var_five = step_input_two["Key07"]

    assert step_input.contains(var_three) == True
    assert step_input.contains(var_five) == False
    assert step_input_two.contains(var_three) == False

def test_placeholder_schema_as_dict():
    workflow_input = ExecutionInput()
    workflow_input["A"]["b"].get("C", float)
    workflow_input["Message"]
    workflow_input["Key01"]["Key02"]
    workflow_input["Key03"]
    workflow_input["Key03"]["Key04"]

    expected_schema = {
        "A": {
            "b": {
                "C": float
            }
        },
        "Message": str,
        "Key01": {
            "Key02": str
        },
        "Key03": {
            "Key04": str
        }
    }

    assert workflow_input.get_schema_as_dict() == expected_schema

def test_placeholder_schema_as_json():
    step_input = StepInput()
    step_input["Response"].get("StatusCode", int)
    step_input["Hello"]["World"]
    step_input["A"]
    step_input["Hello"]["World"].get("Test", str)

    expected_schema = {
        "Response": {
            "StatusCode": "int"
        },
        "Hello": {
            "World": {
                "Test": "str"
            }
        },
        "A": "str"
    }

    assert step_input.get_schema_as_json() == json.dumps(expected_schema)

def test_placeholder_is_empty():
    workflow_input = ExecutionInput()
    placeholder_variable = workflow_input["A"]["B"]["C"]
    assert placeholder_variable._is_empty() == True
    workflow_input["A"]["B"]["C"]["D"]
    assert placeholder_variable._is_empty() == False


def test_placeholder_make_immutable():
    workflow_input = ExecutionInput()
    workflow_input["A"]["b"].get("C", float)
    workflow_input["Message"]
    workflow_input["Key01"]["Key02"]
    workflow_input["Key03"]
    workflow_input["Key03"]["Key04"]

    assert check_immutable(workflow_input) == False

    workflow_input._make_immutable()
    assert check_immutable(workflow_input) == True


def test_placeholder_with_schema():
    test_schema = {
        "A": {
            "B":{
                "C": int
            }
        },
        "Request": {
            "Status": str
        },
        "Hello": float
    }
    workflow_input = ExecutionInput(schema=test_schema)
    assert workflow_input.get_schema_as_dict() == test_schema
    assert workflow_input.immutable == True

    with pytest.raises(ValueError):
        workflow_input["A"]["B"]["D"]
    
    with pytest.raises(ValueError):
        workflow_input["A"]["B"].get("C", float)

def test_workflow_input_jsonpath():
    workflow_input = ExecutionInput()
    placeholder_variable = workflow_input["A"]["b"].get("C", float)
    assert placeholder_variable.to_jsonpath() == "$$.Execution.Input['A']['b']['C']"

def test_step_input_jsonpath():
    step_input = StepInput()
    placeholder_variable = step_input["A"]["b"].get(0, float)
    assert placeholder_variable.to_jsonpath() == "$['A']['b'][0]"

# UTILS

def check_immutable(placeholder):
    if placeholder.immutable is True:
        if placeholder._is_empty():
            return True
        else:
            for k, v in placeholder.store.items():
                return check_immutable(v)
    else:
        return False