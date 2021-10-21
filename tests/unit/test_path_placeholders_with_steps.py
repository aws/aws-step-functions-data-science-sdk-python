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

import boto3
import pytest
from unittest.mock import patch

from stepfunctions.inputs import ExecutionInput, StepInput
from stepfunctions.steps import Pass, Succeed, Wait, Choice, Parallel, Task, Map
from stepfunctions.steps.compute import LambdaStep, GlueStartJobRunStep, BatchSubmitJobStep, EcsRunTaskStep
from stepfunctions.steps.service import DynamoDBGetItemStep, DynamoDBPutItemStep, DynamoDBUpdateItemStep,\
    DynamoDBDeleteItemStep
from stepfunctions.steps.service import (
    EksCallStep,
    EksCreateClusterStep,
    EksCreateFargateProfileStep,
    EksCreateNodeGroupStep,
    EksDeleteClusterStep,
    EksDeleteFargateProfileStep,
    EksDeleteNodegroupStep,
    EksRunJobStep,
)
from stepfunctions.steps.service import EmrCreateClusterStep, EmrTerminateClusterStep, EmrAddStepStep,\
    EmrCancelStepStep, EmrSetClusterTerminationProtectionStep, EmrModifyInstanceFleetByNameStep,\
    EmrModifyInstanceGroupByNameStep
from stepfunctions.steps.service import EventBridgePutEventsStep
from stepfunctions.steps.service import SnsPublishStep, SqsSendMessageStep
from stepfunctions.steps.service import GlueDataBrewStartJobRunStep
from stepfunctions.steps.states import State

@pytest.mark.parametrize("state, state_id, extra_args", [
    # States
    (State, "State", {'state_type': 'Void'}),
    (Pass, "PassState", {}),
    (Choice, "ChoiceState", {}),
    (Succeed, "SucceedState", {}),
    (Parallel, "ParallelState", {}),
    (Task, "TaskState", {}),
    (Wait, "WaitState", {'seconds': 10}),
    (Map, "MapState", {'iterator': Pass('PassState')}),

    # Compute steps
    (LambdaStep, "LambdaStep", {}),
    (EcsRunTaskStep, "EcsRunTaskStep", {}),
    (BatchSubmitJobStep, "BatchSubmitJobStep", {}),
    (GlueStartJobRunStep, "GlueStartJobRunStep", {}),

    # Service steps
    (DynamoDBGetItemStep, "DynamoDBGetItemStep", {}),
    (DynamoDBPutItemStep, "DynamoDBPutItemStep", {}),
    (DynamoDBUpdateItemStep, "DynamoDBUpdateItemStep", {}),
    (DynamoDBDeleteItemStep, "DynamoDBDeleteItemStep", {}),
    (EksCallStep, "EksCallStep", {}),
    (EksCreateClusterStep, "EksCreateClusterStep", {}),
    (EksCreateFargateProfileStep, "EksCreateFargateProfileStep", {}),
    (EksCreateNodeGroupStep, "EksCreateNodeGroupStep", {}),
    (EksDeleteClusterStep, "EksDeleteClusterStep", {}),
    (EksDeleteFargateProfileStep, "EksDeleteFargateProfileStep", {}),
    (EksDeleteNodegroupStep, "EksDeleteNodegroupStep", {}),
    (EksRunJobStep, "EksRunJobStep", {}),
    (EmrCreateClusterStep, "EmrCreateClusterStep", {}),
    (EmrTerminateClusterStep, "EmrTerminateClusterStep", {}),
    (EmrAddStepStep, "EmrAddStepStep", {}),
    (EmrCancelStepStep, "EmrCancelStepStep", {}),
    (EmrSetClusterTerminationProtectionStep, "EmrSetClusterTerminationProtectionStep", {}),
    (EmrModifyInstanceFleetByNameStep, "EmrModifyInstanceFleetByNameStep", {}),
    (EmrModifyInstanceGroupByNameStep, "EmrModifyInstanceGroupByNameStep", {}),
    (EventBridgePutEventsStep, "EventBridgePutEventsStep", {}),
    (SnsPublishStep, "SnsPublishStep", {}),
    (SqsSendMessageStep, "SqsSendMessageStep", {}),
    (GlueDataBrewStartJobRunStep, "GlueDataBrewStartJobRunStep", {})
])
@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_service_step_creation_with_placeholders(state, state_id, extra_args):
    execution_input = ExecutionInput(schema={'input_path': str})
    step_input = StepInput(schema={'output_path': str})
    step = state(state_id, input_path=execution_input['input_path'], output_path=step_input['output_path'], **extra_args)

    assert step.to_dict()['InputPath'] == "$$.Execution.Input['input_path']"
    assert step.to_dict()['OutputPath'] == "$['output_path']"