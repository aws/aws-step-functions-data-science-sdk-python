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

from stepfunctions.steps import Pass, Succeed, Fail, Wait, Choice, ChoiceRule, Parallel, Map, Task, Chain, Graph, FrozenGraph
from stepfunctions.steps.states import State


def test_nested_parallel_example():
    nested_level_1 = Parallel('NestedStateLevel1')
    nested_level_1.add_branch(Succeed('NestedStateLevel2'))

    first_state = Parallel('FirstState')
    first_state.add_branch(nested_level_1)

    result = Graph(first_state, comment='This is a test.', version='1.0', timeout_seconds=3600).to_dict()
    assert result == {
        'StartAt': 'FirstState',
        'Comment': 'This is a test.',
        'Version': '1.0',
        'TimeoutSeconds': 3600,
        'States': {
            'FirstState': {
                'Type': 'Parallel',
                'Branches': [
                    {
                        'StartAt': 'NestedStateLevel1',
                        'States': {
                            'NestedStateLevel1': {
                                'Type': 'Parallel',
                                'Branches': [
                                    {
                                        'StartAt': 'NestedStateLevel2',
                                        'States': {
                                            'NestedStateLevel2': {
                                                'Type': 'Succeed'
                                            }
                                        }
                                    }
                                ],
                                'End': True
                            }
                        }
                    }
                ],
                'End': True
            }
        }
    }

def test_wait_loop():
    first_state = Task('FirstState', resource='arn:aws:lambda:us-east-1:1234567890:function:FirstState')
    retry = Chain([Pass('Retry'), Pass('Cleanup'), first_state])

    choice_state = Choice('Is Completed?')
    choice_state.add_choice(ChoiceRule.BooleanEquals('$.Completed', True), Succeed('Complete'))
    choice_state.add_choice(ChoiceRule.BooleanEquals('$.Completed', False), retry)
    first_state.next(choice_state)

    result = Graph(first_state).to_dict()
    assert result == {
        'StartAt': 'FirstState',
        'States': {
            'FirstState': {
                'Type': 'Task',
                'Resource': 'arn:aws:lambda:us-east-1:1234567890:function:FirstState',
                'Next': 'Is Completed?'
            },
            'Is Completed?': {
                'Type': 'Choice',
                'Choices': [
                    {
                        'Variable': '$.Completed',
                        'BooleanEquals': True,
                        'Next': 'Complete'
                    },
                    {
                        'Variable': '$.Completed',
                        'BooleanEquals': False,
                        'Next': 'Retry'
                    }
                ]
            },
            'Complete': {
                'Type': 'Succeed'
            },
            'Retry': {
                'Type': 'Pass',
                'Next': 'Cleanup',
            },
            'Cleanup': {
                'Type': 'Pass',
                'Next': 'FirstState'
            }
        }
    }

def test_wait_example():
    chain = Chain()
    chain.append(Task('FirstState', resource='arn:aws:lambda:us-east-1:1234567890:function:StartState'))
    chain.append(Wait('wait_using_seconds', seconds=10))
    chain.append(Wait('wait_using_timestamp', timestamp='2015-09-04T01:59:00Z'))
    chain.append(Wait('wait_using_timestamp_path', timestamp_path='$.expirydate'))
    chain.append(Wait('wait_using_seconds_path', seconds_path='$.expiryseconds'))
    chain.append(Task('FinalState', resource='arn:aws:lambda:us-east-1:1234567890:function:EndLambda'))

    result = Graph(chain).to_dict()
    assert result == {
        'StartAt': 'FirstState',
        'States': {
            'FirstState': {
                'Type': 'Task',
                'Resource': 'arn:aws:lambda:us-east-1:1234567890:function:StartState',
                'Next': 'wait_using_seconds'
            },
            'wait_using_seconds': {
                'Type': 'Wait',
                'Seconds': 10,
                'Next': 'wait_using_timestamp'
            },
            'wait_using_timestamp': {
                'Type': 'Wait',
                'Timestamp': '2015-09-04T01:59:00Z',
                'Next': 'wait_using_timestamp_path'
            },
            'wait_using_timestamp_path': {
                'Type': 'Wait',
                'TimestampPath': '$.expirydate',
                'Next': 'wait_using_seconds_path'
            },
            'wait_using_seconds_path': {
                'Type': 'Wait',
                'SecondsPath': '$.expiryseconds',
                'Next': 'FinalState',
            },
            'FinalState': {
                'Type': 'Task',
                'Resource': 'arn:aws:lambda:us-east-1:1234567890:function:EndLambda',
                'End': True
            }
        }
    }

def test_choice_example():
    next_state = Task('NextState', resource='arn:aws:lambda:us-east-1:1234567890:function:NextState')

    choice_state = Choice('ChoiceState')
    choice_state.default_choice(Fail('DefaultState', error='DefaultStateError', cause='No Matches!'))
    choice_state.add_choice(ChoiceRule.NumericEquals(variable='$.foo', value=1), Chain([
        Task('FirstMatchState', resource='arn:aws:lambda:us-east-1:1234567890:function:FirstMatchState'),
        next_state
    ]))

    choice_state.add_choice(ChoiceRule.NumericEquals(variable='$.foo', value=2), Chain([
        Task('SecondMatchState', resource='arn:aws:lambda:us-east-1:1234567890:function:SecondMatchState'),
        next_state
    ]))

    chain = Chain()
    chain.append(Task('FirstState', resource='arn:aws:lambda:us-east-1:1234567890:function:StartLambda'))
    chain.append(choice_state)

    result = Graph(chain).to_dict()
    assert result == {
        'StartAt': 'FirstState',
        'States': {
            'FirstState': {
                'Type': 'Task',
                'Resource': 'arn:aws:lambda:us-east-1:1234567890:function:StartLambda',
                'Next': 'ChoiceState'
            },
            'ChoiceState': {
                'Type': 'Choice',
                'Choices': [
                    {
                        'Variable': '$.foo',
                        'NumericEquals': 1,
                        'Next': 'FirstMatchState'
                    },
                    {
                        'Variable': '$.foo',
                        'NumericEquals': 2,
                        'Next': 'SecondMatchState'
                    }
                ],
                'Default': 'DefaultState'
            },
            'FirstMatchState': {
                'Type': 'Task',
                'Resource': 'arn:aws:lambda:us-east-1:1234567890:function:FirstMatchState',
                'Next': 'NextState'
            },
            'SecondMatchState': {
                'Type': 'Task',
                'Resource': 'arn:aws:lambda:us-east-1:1234567890:function:SecondMatchState',
                'Next': 'NextState'
            },
            'DefaultState': {
                'Type': 'Fail',
                'Error': 'DefaultStateError',
                'Cause': 'No Matches!'
            },
            'NextState': {
                'Type': 'Task',
                'Resource': 'arn:aws:lambda:us-east-1:1234567890:function:NextState',
                'End': True
            }
        }
    }

def test_graph_from_string():
    g = Graph(Chain([Pass('HelloWorld')]))
    g1 = FrozenGraph.from_json(g.to_json())
    assert isinstance(g1, Graph)
    assert g.to_dict() == g1.to_dict()
