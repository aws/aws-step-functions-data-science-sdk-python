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

from stepfunctions.exceptions import DuplicateStatesInChain
from stepfunctions.steps import Pass, Succeed, Fail, Wait, Choice, ChoiceRule, Parallel, Map, Task, Retry, Catch, Chain
from stepfunctions.steps.states import State, to_pascalcase


def test_to_pascalcase():
    assert 'InputPath' == to_pascalcase('input_path')

def test_state_creation():
    state = State(
        state_id='StartState',
        state_type='Void',
        comment = 'This is a comment',
        input_path = '$.Input',
        output_path = '$.Output',
        parameters = {'Key': 'Value'},
        result_path = '$.Result'
    )
    
    assert state.to_dict() == {
        'Type': 'Void',
        'Comment': 'This is a comment',
        'InputPath': '$.Input',
        'OutputPath': '$.Output',
        'Parameters': {
            'Key': 'Value'
        },
        'ResultPath': '$.Result',
        'End': True
    }

    with pytest.raises(TypeError):
        State(state_id='State', unknown_attribute=True)

def test_pass_state_creation():
    pass_state = Pass('Pass', result='Pass')
    assert pass_state.state_id == 'Pass'
    assert pass_state.to_dict() == {
        'Type': 'Pass',
        'Result': 'Pass',
        'End': True
    }
    
def test_verify_pass_state_fields():
    pass_state = Pass(
        state_id='Pass',
        comment='This is a comment',
        parameters={},
        input_path='$.InputPath',
        result_path='$.ResultPath',
        result={}
    )
    assert pass_state.state_id == 'Pass'
    assert pass_state.comment == 'This is a comment'
    assert pass_state.parameters == {}
    assert pass_state.input_path == '$.InputPath'
    assert pass_state.result_path == '$.ResultPath'
    assert pass_state.result == {}

    with pytest.raises(TypeError):
        Pass('Pass', unknown_field='Unknown Field')

def test_succeed_state_creation():
    succeed_state = Succeed(
        state_id='Succeed',
        comment='This is a comment'
    )
    assert succeed_state.state_id == 'Succeed'
    assert succeed_state.comment == 'This is a comment'
    assert succeed_state.to_dict() == {
        'Type': 'Succeed',
        'Comment': 'This is a comment'
    }

def test_verify_succeed_state_fields():
    with pytest.raises(TypeError):
        Succeed('Succeed', unknown_field='Unknown Field')

def test_fail_creation():
    fail_state = Fail(
        state_id='Fail',
        error='ErrorA',
        cause='Kaiju attack',
        comment='This is a comment'
    )
    assert fail_state.state_id == 'Fail'
    assert fail_state.error == 'ErrorA'
    assert fail_state.cause == 'Kaiju attack'
    assert fail_state.comment == 'This is a comment'
    assert fail_state.to_dict() == {
        'Type': 'Fail',
        'Comment': 'This is a comment',
        'Error': 'ErrorA',
        'Cause': 'Kaiju attack'
    }

def test_verify_fail_state_fields():
    with pytest.raises(TypeError):
        Fail('Succeed', unknown_field='Unknown Field')

def test_wait_state_creation():
    wait_state = Wait(
        state_id='Wait',
        seconds=10
    )
    assert wait_state.state_id == 'Wait'
    assert wait_state.seconds == 10
    assert wait_state.to_dict() == {
        'Type': 'Wait',
        'Seconds': 10,
        'End': True
    }

    wait_state = Wait(
        state_id='Wait',
        seconds_path='$.SecondsPath'
    )
    assert wait_state.state_id == 'Wait'
    assert wait_state.seconds_path == '$.SecondsPath'
    assert wait_state.to_dict() == {
        'Type': 'Wait',
        'SecondsPath': '$.SecondsPath',
        'End': True
    }

def test_verify_wait_state_fields():
    with pytest.raises(ValueError):
        Wait(
            state_id='Wait',
            seconds=10,
            seconds_path='$.SecondsPath'
        )

def test_choice_state_creation():
    choice_state = Choice('Choice', input_path='$.Input')
    choice_state.add_choice(ChoiceRule.StringEquals("$.StringVariable1", "ABC"), Pass("End State 1"))
    choice_state.add_choice(ChoiceRule.StringLessThanEquals("$.StringVariable2", "ABC"), Pass("End State 2"))
    choice_state.default_choice(Pass('End State 3'))
    assert choice_state.state_id == 'Choice'
    assert len(choice_state.choices) == 2
    assert choice_state.default.state_id == 'End State 3'
    assert choice_state.to_dict() == {
        'Type': 'Choice',
        'InputPath': '$.Input',
        'Choices': [
            {
                'Variable': '$.StringVariable1',
                'StringEquals': 'ABC',
                'Next': 'End State 1'
            },
            {
                'Variable': '$.StringVariable2',
                'StringLessThanEquals': 'ABC',
                'Next': 'End State 2'
            }
        ],
        'Default': 'End State 3'
    }

    with pytest.raises(TypeError):
        Choice('Choice', unknown_field='Unknown Field')

def test_task_state_creation():
    task_state = Task('Task', resource='arn:aws:lambda:us-east-1:1234567890:function:StartLambda')
    task_state.add_retry(Retry(error_equals=['ErrorA', 'ErrorB'], interval_seconds=1, max_attempts=2, backoff_rate=2))
    task_state.add_retry(Retry(error_equals=['ErrorC'], interval_seconds=5))
    task_state.add_catch(Catch(error_equals=['States.ALL'], next_step=Pass('End State')))
    assert task_state.type == 'Task'
    assert len(task_state.retries) == 2
    assert len(task_state.catches) == 1
    assert task_state.to_dict() == {
        'Type': 'Task',
        'Resource': 'arn:aws:lambda:us-east-1:1234567890:function:StartLambda',
        'Retry': [
            {
                'ErrorEquals': ['ErrorA', 'ErrorB'],
                'IntervalSeconds': 1,
                'BackoffRate': 2,
                'MaxAttempts': 2
            },
            {
                'ErrorEquals': ['ErrorC'],
                'IntervalSeconds': 5
            }
        ],
        'Catch': [
            {
                'ErrorEquals': ['States.ALL'],
                'Next': 'End State'
            }
        ],
        'End': True
    }

def test_parallel_state_creation():
    parallel_state = Parallel('Parallel')
    parallel_state.add_branch(Pass('Branch 1'))
    parallel_state.add_branch(Pass('Branch 2'))
    parallel_state.add_branch(Pass('Branch 3'))
    assert parallel_state.type == 'Parallel'
    assert len(parallel_state.branches) == 3
    assert parallel_state.to_dict() == {
        'Type': 'Parallel',
        'Branches': [
            {
                'StartAt': 'Branch 1',
                'States': {
                    'Branch 1': {
                        'Type': 'Pass',
                        'End': True
                    }
                }
            },
            {
                'StartAt': 'Branch 2',
                'States': {
                    'Branch 2': {
                        'Type': 'Pass',
                        'End': True
                    }
                }
            },
            {
                'StartAt': 'Branch 3',
                'States': {
                    'Branch 3': {
                        'Type': 'Pass',
                        'End': True
                    }
                }
            }
        ],
        'End': True
    }

def test_map_state_creation():
    map_state = Map('Map', iterator=Pass('FirstIteratorState'), items_path='$', max_concurrency=0)
    assert map_state.to_dict() == {
        'Type': 'Map',
        'ItemsPath': '$',
        'Iterator': {
            'StartAt': 'FirstIteratorState',
            'States': {
                'FirstIteratorState': {
                    'Type': 'Pass',
                    'End': True
                }
            }
        },
        'MaxConcurrency': 0,
        'End': True
    }

def test_nested_chain_is_now_allowed():
    chain = Chain([Chain([Pass('S1')])])

def test_catch_creation():
    catch = Catch(error_equals=['States.ALL'], next_step=Fail('End'))
    assert catch.to_dict() == {
        'ErrorEquals': ['States.ALL'],
        'Next': 'End'
    }

def test_append_states_after_terminal_state_will_fail():
    with pytest.raises(ValueError):
        chain = Chain()
        chain.append(Pass('Pass'))
        chain.append(Fail('Fail'))
        chain.append(Pass('Pass2'))
    
    with pytest.raises(ValueError):
        chain = Chain()
        chain.append(Pass('Pass'))
        chain.append(Succeed('Succeed'))
        chain.append(Pass('Pass2'))
    
    with pytest.raises(ValueError):
        chain = Chain()
        chain.append(Pass('Pass'))
        chain.append(Choice('Choice'))
        chain.append(Pass('Pass2'))


def test_chaining_steps():
    s1 = Pass('Step - One')
    s2 = Pass('Step - Two')
    s3 = Pass('Step - Three')

    Chain([s1, s2])
    assert s1.next_step == s2
    assert s2.next_step is None

    chain1 = Chain([s2, s3])
    assert s2.next_step == s3

    chain2 = Chain([s1, s3])
    assert s1.next_step == s3
    assert s2.next_step == s1.next_step
    with pytest.raises(DuplicateStatesInChain):
        chain2.append(s3)

    with pytest.raises(DuplicateStatesInChain):
        chain3 = Chain([chain1, chain2])
    
    s1.next(s2)
    chain3 = Chain([s3, s1])
    assert chain3.steps == [s3, s1]
    assert s3.next_step == s1
    assert s1.next_step == s2
    assert s2.next_step == s3

    Chain([Chain([s3]), Chain([s1])])

    with pytest.raises(DuplicateStatesInChain):
        Chain([Chain([s1, s2, s1]), s3])
        Chain([s1, s2, s1, s3])
    Chain([Chain([s1, s2]), s3])
    assert s1.next_step == s2
    assert s2.next_step == s3

def test_catch_fail_for_unsupported_state():
    s1 = Pass('Step - One')

    with pytest.raises(ValueError):
        s1.add_retry(Retry(error_equals=['ErrorA', 'ErrorB'], interval_seconds=1, max_attempts=2, backoff_rate=2))


def test_retry_fail_for_unsupported_state():

    c1 = Choice('My Choice')
    
    with pytest.raises(ValueError):
        c1.add_catch(Catch(error_equals=["States.NoChoiceMatched"], next_step=Fail("ChoiceFailed")))