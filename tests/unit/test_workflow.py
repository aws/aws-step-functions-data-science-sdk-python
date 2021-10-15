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
import uuid
import boto3
import yaml
import json

from datetime import datetime
from unittest.mock import MagicMock, Mock
from stepfunctions import steps
from stepfunctions.exceptions import WorkflowNotFound, MissingRequiredParameter
from stepfunctions.workflow import Workflow, Execution, ExecutionStatus


state_machine_name = 'HelloWorld'
state_machine_arn = 'arn:aws:states:us-east-1:1234567890:stateMachine:HelloWorld'
role_arn = 'arn:aws:iam::1234567890:role/service-role/StepFunctionsRole'
execution_arn = 'arn:aws:states:us-east-1:1234567890:execution:HelloWorld:execution-1'
definition = steps.Chain([steps.Pass('HelloWorld'), steps.Succeed('Complete')])


@pytest.fixture
def client():
    sfn = boto3.client('stepfunctions')
    sfn.describe_state_machine = MagicMock(return_value={
        'creationDate': datetime(2019, 9, 9, 9, 59, 59, 276000),
        'definition': steps.Graph(definition).to_json(),
        'name': state_machine_name,
        'roleArn': role_arn,
        'stateMachineArn': state_machine_arn,
        'status': 'ACTIVE'
    })
    sfn.create_state_machine = MagicMock(return_value={
        'creationDate': datetime.now(),
        'stateMachineArn': state_machine_arn
    })
    sfn.delete_state_machine = MagicMock(return_value=None)
    sfn.start_execution = MagicMock(return_value={
        'executionArn': execution_arn,
        'startDate': datetime.now(),
        'stateMachineArn': state_machine_arn,
        'status': 'RUNNING'
    })
    return sfn


@pytest.fixture
def workflow(client):
    workflow = Workflow(
        name=state_machine_name,
        definition=definition,
        role=role_arn,
        client=client
    )
    workflow.create()
    return workflow


def test_workflow_creation(client, workflow):
    assert workflow.state_machine_arn == state_machine_arn


def test_workflow_creation_failure_duplicate_state_ids(client):
    improper_definition = steps.Chain([steps.Pass('HelloWorld'), steps.Succeed('HelloWorld')])
    with pytest.raises(ValueError):
        workflow = Workflow(
            name=state_machine_name,
            definition=improper_definition,
            role=role_arn,
            client=client
        )


# calling update() before create()
def test_workflow_update_when_statemachinearn_is_none(client):
    workflow = Workflow(
        name=state_machine_name,
        definition=definition,
        role=role_arn,
        client=client
    )
    new_definition = steps.Pass('HelloWorld')
    with pytest.raises(WorkflowNotFound):
        workflow.update(definition=new_definition)


# calling update() after create() without arguments
def test_workflow_update_when_arguments_are_missing(client, workflow):
    with pytest.raises(MissingRequiredParameter):
        workflow.update()


# calling update() after create()
def test_workflow_update(client, workflow):
    client.update_state_machine = MagicMock(return_value={
        'updateDate': datetime.now()
    })
    new_definition = steps.Pass('HelloWorld')
    new_role = 'arn:aws:iam::1234567890:role/service-role/StepFunctionsRoleNew'
    assert workflow.update(definition=new_definition, role=new_role) == state_machine_arn


def test_attach_existing_workflow(client):
    workflow = Workflow.attach(state_machine_arn, client)
    assert workflow.name == state_machine_name
    assert workflow.role == role_arn
    assert workflow.state_machine_arn == state_machine_arn


def test_workflow_list_executions(client, workflow):
    paginator = client.get_paginator('list_executions')
    paginator.paginate = MagicMock(return_value=[
        {
            'executions': [
                {
                    'stateMachineArn': state_machine_arn,
                    'executionArn': execution_arn,
                    'startDate': datetime.now(),
                    'status': 'RUNNING',
                    'name': 'HelloWorld'
                }
            ]
        }
    ])
    client.get_paginator = MagicMock(return_value=paginator)

    execution = workflow.execute()
    assert execution.workflow.state_machine_arn == workflow.state_machine_arn
    assert execution.execution_arn == execution_arn

    executions = workflow.list_executions()
    assert len(executions) == 1
    assert isinstance(executions[0], Execution)

    workflow.state_machine_arn = None
    assert workflow.list_executions() == []


def test_workflow_makes_deletion_call(client, workflow):
    client.delete_state_machine = MagicMock(return_value=None)
    workflow.delete()

    client.delete_state_machine.assert_called_once_with(stateMachineArn=state_machine_arn)


def test_workflow_execute_creation(client, workflow):
    execution = workflow.execute()
    assert execution.workflow.state_machine_arn == state_machine_arn
    assert execution.execution_arn == execution_arn
    assert execution.status == ExecutionStatus.Running

    client.start_execution = MagicMock(return_value={
        'executionArn': 'arn:aws:states:us-east-1:1234567890:execution:HelloWorld:TestRun',
        'startDate': datetime.now()
    })

    execution = workflow.execute(name='TestRun', inputs={})
    client.start_execution.assert_called_once_with(
        stateMachineArn=state_machine_arn,
        name='TestRun',
        input='{}'
    )


def test_workflow_execute_when_statemachinearn_is_none(client, workflow):
    workflow.state_machine_arn = None
    with pytest.raises(WorkflowNotFound):
        workflow.execute()


def test_execution_makes_describe_call(client, workflow):
    execution = workflow.execute()

    client.describe_execution = MagicMock(return_value={})
    execution.describe()

    client.describe_execution.assert_called_once()


def test_execution_makes_stop_call(client, workflow):
    execution = workflow.execute()

    client.stop_execution = MagicMock(return_value={})

    execution.stop()
    client.stop_execution.assert_called_with(
        executionArn=execution_arn
    )

    execution.stop(cause='Test', error='Error')
    client.stop_execution.assert_called_with(
        executionArn=execution_arn,
        cause='Test',
        error='Error'
    )


def test_execution_list_events(client, workflow):
    paginator = client.get_paginator('get_execution_history')
    paginator.paginate = MagicMock(return_value=[
        {
            'events': [
                {
                    'timestamp': datetime(2019, 1, 1),
                    'type': 'TaskFailed',
                    'id': 123,
                    'previousEventId': 456,
                    'taskFailedEventDetails': {
                        'resourceType': 'type',
                        'resource': 'resource',
                        'error': 'error',
                        'cause': 'test'
                    }
                }
            ],
            'NextToken': 'Token'
        }
    ])
    client.get_paginator = MagicMock(return_value=paginator)

    execution = workflow.execute()
    execution.list_events(max_items=999, reverse_order=True)

    paginator.paginate.assert_called_with(
        executionArn=execution_arn,
        reverseOrder=True,
        PaginationConfig={
            'MaxItems': 999,
            'PageSize': 1000
        }
    )


def test_list_workflows(client):
    paginator = client.get_paginator('list_state_machines')
    paginator.paginate = MagicMock(return_value=[
        {
            'stateMachines': [
                {
                    'stateMachineArn': state_machine_arn,
                    'name': state_machine_name,
                    'creationDate': datetime(2019, 1, 1)
                }
            ],
            'NextToken': 'Token'
        }
    ])

    client.get_paginator = MagicMock(return_value=paginator)
    workflows = Workflow.list_workflows(max_items=999, client=client)

    paginator.paginate.assert_called_with(
        PaginationConfig={
            'MaxItems': 999,
            'PageSize': 1000
        }
    )


def test_cloudformation_export_with_simple_definition(workflow):
    cfn_template = workflow.get_cloudformation_template()
    cfn_template = yaml.safe_load(cfn_template)
    assert 'StateMachineComponent' in cfn_template['Resources']
    assert workflow.role == cfn_template['Resources']['StateMachineComponent']['Properties']['RoleArn']
    assert cfn_template['Description'] == "CloudFormation template for AWS Step Functions - State Machine"


def test_cloudformation_export_with_sagemaker_execution_role(workflow):
    workflow.definition.to_dict = MagicMock(return_value={
        'StartAt': 'Training',
        'States': {
            'Training': {
                'Type': 'Task',
                'Parameters': {
                    'AlgorithmSpecification': {
                        'TrainingImage': '382416733822.dkr.ecr.us-east-1.amazonaws.com/pca:1',
                        'TrainingInputMode': 'File'
                    },
                    'OutputDataConfig': {
                        'S3OutputPath': 's3://sagemaker/models'
                    },
                    'RoleArn': 'arn:aws:iam::1234567890:role/service-role/AmazonSageMaker-ExecutionRole',
                },
                'Resource': 'arn:aws:states:::sagemaker:createTrainingJob.sync',
                'End': True
            }
        }
    })
    cfn_template = workflow.get_cloudformation_template(description="CloudFormation template with Sagemaker role")
    cfn_template = yaml.safe_load(cfn_template)
    assert json.dumps(workflow.definition.to_dict(), indent=2) == cfn_template['Resources']['StateMachineComponent']['Properties']['DefinitionString']
    assert workflow.role == cfn_template['Resources']['StateMachineComponent']['Properties']['RoleArn']
    assert cfn_template['Description'] == "CloudFormation template with Sagemaker role"
