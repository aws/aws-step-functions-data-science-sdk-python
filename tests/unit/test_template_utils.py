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

from stepfunctions.steps.states import Task
from stepfunctions.template.utils import (
    replace_parameters_with_context_object,
    replace_parameters_with_jsonpath
)


def test_context_object_replacement():
    task = Task('LambdaTask', parameters={
        'InputObject': 'Result',
        'OutputObject': {
            'Location': 'Unknown'
        }
    })

    task.update_parameters(replace_parameters_with_context_object(task))

    assert task.parameters == {
        'InputObject.$': "$$.Execution.Input['LambdaTask'].InputObject",
        'OutputObject.$': "$$.Execution.Input['LambdaTask'].OutputObject",
    }

def test_jsonpath_replacement():
    task = Task('LambdaTask', parameters={
        'InputObject': 'Result',
        'OutputObject': {
            'Location': {
                'Country': 'Unknown',
                'City': 'Unknown'
            },
            'Coordinates': {
                'Latitude': 0,
                'Longitude': 0
            }
        }
    })

    params = replace_parameters_with_jsonpath(task, {
        'InputObject.$': '$.InputObject',
        'OutputObject': {
            'Location.$': '$.OutputLocation',
            'Coordinates': {
                'Latitude.$': '$.Latitude',
                'Longitude': 0
            }
        }
    })

    print(params)

    assert params == {
        'InputObject.$': '$.InputObject',
        'OutputObject': {
            'Location.$': '$.OutputLocation',
            'Coordinates': {
                'Latitude.$': '$.Latitude',
                'Longitude': 0
            }
        }
    }
