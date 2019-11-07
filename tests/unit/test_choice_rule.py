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

from stepfunctions.steps import Pass, Succeed, Fail, Wait, ChoiceRule


def test_variable_must_start_with_prefix():
    with pytest.raises(ValueError):
        ChoiceRule.StringEquals('Variable', '42')

def test_variable_value_must_be_consistent():
    string_functions = (
        'StringEquals',
        'StringLessThan',
        'StringGreaterThan',
        'StringLessThanEquals',
        'StringGreaterThanEquals',
    )
    for string_function in string_functions:
        func = getattr(ChoiceRule, string_function)
        with pytest.raises(ValueError):
            func('$.Variable', 42)

    numeric_functions = (
        'NumericEquals',
        'NumericLessThan',
        'NumericGreaterThan',
        'NumericLessThanEquals',
        'NumericGreaterThanEquals',
    )
    for numeric_function in numeric_functions:
        func = getattr(ChoiceRule, numeric_function)
        with pytest.raises(ValueError):
            func('$.Variable', 'ABC')
    
    with pytest.raises(ValueError):
        ChoiceRule.BooleanEquals('$.Variable', 42)

    timestamp_functions = (
        'TimestampEquals',
        'TimestampLessThan',
        'TimestampGreaterThan',
        'TimestampLessThanEquals',
        'TimestampGreaterThanEquals',
    )
    for timestamp_function in timestamp_functions:
        func = getattr(ChoiceRule, timestamp_function)
        with pytest.raises(ValueError):
            func('$.Variable', True)

def test_rule_serialization():
    bool_rule = ChoiceRule.BooleanEquals('$.BooleanVariable', True)
    assert bool_rule.to_dict() == {
        'Variable': '$.BooleanVariable',
        'BooleanEquals': True
    }

    string_rule = ChoiceRule.StringEquals('$.StringVariable', 'ABC')
    assert string_rule.to_dict() == {
        'Variable': '$.StringVariable',
        'StringEquals': 'ABC'
    }

    and_rule = ChoiceRule.And([bool_rule, string_rule])
    assert and_rule.to_dict() == {
        'And': [
            {
                'Variable': '$.BooleanVariable',
                'BooleanEquals': True
            },
            {
                'Variable': '$.StringVariable',
                'StringEquals': 'ABC'
            }
        ]
    }

    not_rule = ChoiceRule.Not(string_rule)
    assert not_rule.to_dict() == {
        'Not': {
            'Variable': '$.StringVariable',
            'StringEquals': 'ABC'
        }
    }

    compound_rule = ChoiceRule.Or([and_rule, not_rule])
    assert compound_rule.to_dict() == {
        'Or': [
            {
                'And': [{
                    'Variable': '$.BooleanVariable',
                    'BooleanEquals': True
                },
                {
                    'Variable': '$.StringVariable',
                    'StringEquals': 'ABC'
                }],
            },
            {
                'Not': {
                    'Variable': '$.StringVariable',
                    'StringEquals': 'ABC'
                }
            }
        ]
    }
