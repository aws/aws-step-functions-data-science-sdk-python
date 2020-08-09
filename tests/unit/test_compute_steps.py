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

from stepfunctions.exceptions import ForbiddenValueParameter
from stepfunctions.steps.compute import LambdaStep, GlueStartJobRunStep, BatchSubmitJobStep, EcsRunTaskStep
from stepfunctions.steps.states import IntegrationPattern


def test_lambda_step_creation():
    step = LambdaStep('Echo')

    assert step.to_dict() == {
        'Type': 'Task',
        'Resource': 'arn:aws:states:::lambda:invoke',
        'End': True
    }

    step = LambdaStep('lambda', integration_pattern=IntegrationPattern.WaitForCallback, parameters={
        'Payload': {
            'model.$': '$.new_model',
            'token.$': '$$.Task.Token'
        }
    })

    assert step.to_dict() == {
        'Type': 'Task',
        'Resource': 'arn:aws:states:::lambda:invoke.waitForTaskToken',
        'Parameters': {
            'Payload': {
                'model.$': '$.new_model',
                'token.$': '$$.Task.Token'
            },
        },
        'End': True
    }

    with pytest.raises(ForbiddenValueParameter):
        step = LambdaStep('Echo', integration_pattern=IntegrationPattern.RunAJob)


def test_glue_start_job_run_step_creation():
    step = GlueStartJobRunStep('Glue Job', integration_pattern=IntegrationPattern.RequestResponse)

    assert step.to_dict() == {
        'Type': 'Task',
        'Resource': 'arn:aws:states:::glue:startJobRun',
        'End': True
    }

    step = GlueStartJobRunStep('Glue Job', parameters={
        'JobName': 'Job'
    })

    assert step.to_dict() == {
        'Type': 'Task',
        'Resource': 'arn:aws:states:::glue:startJobRun.sync',
        'Parameters': {
            'JobName': 'Job',
        },
        'End': True
    }

    with pytest.raises(ForbiddenValueParameter):
        step = GlueStartJobRunStep('Glue Job', integration_pattern=IntegrationPattern.WaitForCallback)


def test_batch_submit_job_step_creation():
    step = BatchSubmitJobStep('Batch Job', integration_pattern=IntegrationPattern.RequestResponse)

    assert step.to_dict() == {
        'Type': 'Task',
        'Resource': 'arn:aws:states:::batch:submitJob',
        'End': True
    }

    step = BatchSubmitJobStep('Batch Job', parameters={
        'JobName': 'Job',
        'JobQueue': 'JobQueue'
    })

    assert step.to_dict() == {
        'Type': 'Task',
        'Resource': 'arn:aws:states:::batch:submitJob.sync',
        'Parameters': {
            'JobName': 'Job',
            'JobQueue': 'JobQueue'
        },
        'End': True
    }

    with pytest.raises(ForbiddenValueParameter):
        step = BatchSubmitJobStep('Batch Job', integration_pattern=IntegrationPattern.WaitForCallback)


def test_ecs_run_task_step_creation():
    step = EcsRunTaskStep('Ecs Job')

    assert step.to_dict() == {
        'Type': 'Task',
        'Resource': 'arn:aws:states:::ecs:runTask',
        'End': True
    }

    step = EcsRunTaskStep('Ecs Job', integration_pattern=IntegrationPattern.RunAJob, parameters={
        'TaskDefinition': 'Task'
    })

    assert step.to_dict() == {
        'Type': 'Task',
        'Resource': 'arn:aws:states:::ecs:runTask.sync',
        'Parameters': {
            'TaskDefinition': 'Task'
        },
        'End': True
    }

    step = EcsRunTaskStep('Ecs Job', integration_pattern=IntegrationPattern.WaitForCallback, parameters={
        'TaskDefinition': 'Task'
    })

    assert step.to_dict() == {
        'Type': 'Task',
        'Resource': 'arn:aws:states:::ecs:runTask.waitForTaskToken',
        'Parameters': {
            'TaskDefinition': 'Task'
        },
        'End': True
    }