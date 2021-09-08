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

from stepfunctions.inputs import ExecutionInput, StepInput, StepResult


@pytest.mark.parametrize("placeholder", [StepInput(), StepResult(), ExecutionInput()])
def test_placeholder_creation_with_subscript_operator(placeholder):
    placeholder_variable = placeholder["A"]
    assert placeholder_variable.name == "A"
    assert placeholder_variable.type is None


@pytest.mark.parametrize("placeholder", [StepInput(), StepResult(), ExecutionInput()])
def test_placeholder_creation_with_type(placeholder):
    placeholder_variable = placeholder["A"]["b"].get("C", float)
    assert placeholder_variable.name == "C"
    assert placeholder_variable.type == float


@pytest.mark.parametrize("placeholder", [StepInput(), StepResult(), ExecutionInput()])
def test_placeholder_creation_with_int_key(placeholder):
    placeholder_variable = placeholder["A"][0]
    assert placeholder_variable.name == 0
    assert placeholder_variable.type == None


@pytest.mark.parametrize("placeholder", [StepInput(), StepResult(), ExecutionInput()])
def test_placeholder_creation_with_invalid_key(placeholder):
    with pytest.raises(ValueError):
        placeholder["A"][1.3]
    with pytest.raises(ValueError):
        placeholder["A"].get(1.2, str)


@pytest.mark.parametrize("placeholder", [StepInput(), StepResult(), ExecutionInput()])
def test_placeholder_creation_failure_with_type(placeholder):
    placeholder_variable = placeholder["A"]["b"].get("C", float)
    with pytest.raises(ValueError):
        placeholder["A"]["b"].get("C", int)


@pytest.mark.parametrize("placeholder", [StepInput(), StepResult(), ExecutionInput()])
def test_placeholder_path(placeholder):
    placeholder_variable = placeholder["A"]["b"]["C"]
    expected_path = ["A", "b", "C"]
    assert placeholder_variable._get_path() == expected_path


@pytest.mark.parametrize("placeholder", [StepInput(), StepResult(), ExecutionInput()])
def test_placeholder_contains(placeholder):
    var_one = placeholder["Key01"]
    var_two = placeholder["Key02"]["Key03"]
    var_three = placeholder["Key01"]["Key04"]
    var_four = placeholder["Key05"]

    placeholder_two = StepInput()
    var_five = placeholder_two["Key07"]

    assert placeholder.contains(var_three) == True
    assert placeholder.contains(var_five) == False
    assert placeholder_two.contains(var_three) == False


@pytest.mark.parametrize("placeholder", [StepInput(), StepResult(), ExecutionInput()])
def test_placeholder_schema_as_dict(placeholder):
    placeholder["A"]["b"].get("C", float)
    placeholder["Message"]
    placeholder["Key01"]["Key02"]
    placeholder["Key03"]
    placeholder["Key03"]["Key04"]

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

    assert placeholder.get_schema_as_dict() == expected_schema


@pytest.mark.parametrize("placeholder", [StepInput(), StepResult(), ExecutionInput()])
def test_placeholder_schema_as_json(placeholder):
    placeholder["Response"].get("StatusCode", int)
    placeholder["Hello"]["World"]
    placeholder["A"]
    placeholder["Hello"]["World"].get("Test", str)

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

    assert placeholder.get_schema_as_json() == json.dumps(expected_schema)


@pytest.mark.parametrize("placeholder", [StepInput(), StepResult(), ExecutionInput()])
def test_placeholder_is_empty(placeholder):
    placeholder_variable = placeholder["A"]["B"]["C"]
    assert placeholder_variable._is_empty() == True
    placeholder["A"]["B"]["C"]["D"]
    assert placeholder_variable._is_empty() == False


@pytest.mark.parametrize("placeholder", [StepInput(), StepResult(), ExecutionInput()])
def test_placeholder_make_immutable(placeholder):
    placeholder["A"]["b"].get("C", float)
    placeholder["Message"]
    placeholder["Key01"]["Key02"]
    placeholder["Key03"]
    placeholder["Key03"]["Key04"]

    assert check_immutable(placeholder) == False

    placeholder._make_immutable()
    assert check_immutable(placeholder) == True


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


def test_step_result_jsonpath():
    step_result = StepResult()
    placeholder_variable = step_result["A"]["b"].get(0, float)
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
