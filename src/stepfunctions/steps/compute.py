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

from stepfunctions.steps.states import IntegrationPattern
from stepfunctions.steps.states import Task


class LambdaStep(Task):

    """
    Creates a Task state to invoke an AWS Lambda function. See `Invoke Lambda with Step Functions <https://docs.aws.amazon.com/step-functions/latest/dg/connect-lambda.html>`_ for more details.
    """

    def __init__(self, state_id, integration_pattern=IntegrationPattern.RequestResponse, **kwargs):
        """
        Args:
            state_id (str): State name whose length **must be** less than or equal to 128 unicode characters. State names **must be** unique within the scope of the whole state machine.
            integration_pattern(stepfunctions.states.IntegrationPattern, optional): Enum value set to RunAJob if the task should wait to complete before proceeding to the next step in the workflow, set to WaitForCallback if the Task state should wait for callback to resume the operation or set to RequestResponse if the Task should wait for HTTP response (default: RequestResponse)
            timeout_seconds (int, optional): Positive integer specifying timeout for the state in seconds. If the state runs longer than the specified timeout, then the interpreter fails the state with a `States.Timeout` Error Name. (default: 60)
            heartbeat_seconds (int, optional): Positive integer specifying heartbeat timeout for the state in seconds. This value should be lower than the one specified for `timeout_seconds`. If more time than the specified heartbeat elapses between heartbeats from the task, then the interpreter fails the state with a `States.Timeout` Error Name.
            comment (str, optional): Human-readable comment or description. (default: None)
            input_path (str, optional): Path applied to the state’s raw input to select some or all of it; that selection is used by the state. (default: '$')
            parameters (dict, optional): The value of this field becomes the effective input for the state.
            result_path (str, optional): Path specifying the raw input’s combination with or replacement by the state’s result. (default: '$')
            output_path (str, optional): Path applied to the state’s output after the application of `result_path`, producing the effective output which serves as the raw input for the next state. (default: '$')
        """
        self._valid_patterns = [IntegrationPattern.RequestResponse, IntegrationPattern.WaitForCallback]
        self._integration_pattern = integration_pattern
        action = "lambda:invoke"
        step_name = "Lambda"
        super(LambdaStep, self).__init__(state_id, action, step_name, **kwargs)


class GlueStartJobRunStep(Task):

    """
    Creates a Task state to run an AWS Glue job. See `Manage AWS Glue Jobs with Step Functions <https://docs.aws.amazon.com/step-functions/latest/dg/connect-glue.html>`_ for more details.
    """

    def __init__(self, state_id, integration_pattern=IntegrationPattern.RunAJob, **kwargs):
        """
        Args:
            state_id (str): State name whose length **must be** less than or equal to 128 unicode characters. State names **must be** unique within the scope of the whole state machine.
            integration_pattern(stepfunctions.states.IntegrationPattern, optional): Enum value set to RunAJob if the task should wait to complete before proceeding to the next step in the workflow, set to WaitForCallback if the Task state should wait for callback to resume the operation or set to RequestResponse if the Task should wait for HTTP response (default: RequestResponse)
            timeout_seconds (int, optional): Positive integer specifying timeout for the state in seconds. If the state runs longer than the specified timeout, then the interpreter fails the state with a `States.Timeout` Error Name. (default: 60)
            heartbeat_seconds (int, optional): Positive integer specifying heartbeat timeout for the state in seconds. This value should be lower than the one specified for `timeout_seconds`. If more time than the specified heartbeat elapses between heartbeats from the task, then the interpreter fails the state with a `States.Timeout` Error Name.
            comment (str, optional): Human-readable comment or description. (default: None)
            input_path (str, optional): Path applied to the state’s raw input to select some or all of it; that selection is used by the state. (default: '$')
            parameters (dict, optional): The value of this field becomes the effective input for the state.
            result_path (str, optional): Path specifying the raw input’s combination with or replacement by the state’s result. (default: '$')
            output_path (str, optional): Path applied to the state’s output after the application of `result_path`, producing the effective output which serves as the raw input for the next state. (default: '$')
        """
        self._valid_patterns = [IntegrationPattern.RequestResponse, IntegrationPattern.RunAJob]
        self._integration_pattern = integration_pattern
        super(GlueStartJobRunStep, self).__init__(state_id, "glue:startJobRun", "AWS Glue", **kwargs)


class BatchSubmitJobStep(Task):

    """
    Creates a Task State to start an AWS Batch job. See `Manage AWS Batch with Step Functions <https://docs.aws.amazon.com/step-functions/latest/dg/connect-batch.html>`_ for more details.
    """

    def __init__(self, state_id, integration_pattern=IntegrationPattern.RunAJob, **kwargs):
        """
        Args:
            state_id (str): State name whose length **must be** less than or equal to 128 unicode characters. State names **must be** unique within the scope of the whole state machine.
            integration_pattern(stepfunctions.states.IntegrationPattern, optional): Enum value set to RunAJob if the task should wait to complete before proceeding to the next step in the workflow, set to WaitForCallback if the Task state should wait for callback to resume the operation or set to RequestResponse if the Task should wait for HTTP response (default: RequestResponse)
            timeout_seconds (int, optional): Positive integer specifying timeout for the state in seconds. If the state runs longer than the specified timeout, then the interpreter fails the state with a `States.Timeout` Error Name. (default: 60)
            heartbeat_seconds (int, optional): Positive integer specifying heartbeat timeout for the state in seconds. This value should be lower than the one specified for `timeout_seconds`. If more time than the specified heartbeat elapses between heartbeats from the task, then the interpreter fails the state with a `States.Timeout` Error Name.
            comment (str, optional): Human-readable comment or description. (default: None)
            input_path (str, optional): Path applied to the state’s raw input to select some or all of it; that selection is used by the state. (default: '$')
            parameters (dict, optional): The value of this field becomes the effective input for the state.
            result_path (str, optional): Path specifying the raw input’s combination with or replacement by the state’s result. (default: '$')
            output_path (str, optional): Path applied to the state’s output after the application of `result_path`, producing the effective output which serves as the raw input for the next state. (default: '$')
        """
        self._valid_patterns = [IntegrationPattern.RequestResponse, IntegrationPattern.RunAJob]
        self._integration_pattern = integration_pattern
        super(BatchSubmitJobStep, self).__init__(state_id, "batch:submitJob", "AWS Batch", **kwargs)


class EcsRunTaskStep(Task):

    """
    Creates a Task State to run Amazon ECS or Fargate Tasks. See `Manage Amazon ECS or Fargate Tasks with Step Functions <https://docs.aws.amazon.com/step-functions/latest/dg/connect-ecs.html>`_ for more details.
    """

    def __init__(self, state_id, integration_pattern=IntegrationPattern.RequestResponse, **kwargs):
        """
        Args:
            state_id (str): State name whose length **must be** less than or equal to 128 unicode characters. State names **must be** unique within the scope of the whole state machine.
            integration_pattern(stepfunctions.states.IntegrationPattern, optional): Enum value set to RunAJob if the task should wait to complete before proceeding to the next step in the workflow, set to WaitForCallback if the Task state should wait for callback to resume the operation or set to RequestResponse if the Task should wait for HTTP response (default: RequestResponse)            timeout_seconds (int, optional): Positive integer specifying timeout for the state in seconds. If the state runs longer than the specified timeout, then the interpreter fails the state with a `States.Timeout` Error Name. (default: 60)
            heartbeat_seconds (int, optional): Positive integer specifying heartbeat timeout for the state in seconds. This value should be lower than the one specified for `timeout_seconds`. If more time than the specified heartbeat elapses between heartbeats from the task, then the interpreter fails the state with a `States.Timeout` Error Name.
            comment (str, optional): Human-readable comment or description. (default: None)
            input_path (str, optional): Path applied to the state’s raw input to select some or all of it; that selection is used by the state. (default: '$')
            parameters (dict, optional): The value of this field becomes the effective input for the state.
            result_path (str, optional): Path specifying the raw input’s combination with or replacement by the state’s result. (default: '$')
            output_path (str, optional): Path applied to the state’s output after the application of `result_path`, producing the effective output which serves as the raw input for the next state. (default: '$')
        """
        self._valid_patterns = [IntegrationPattern.RequestResponse, IntegrationPattern.RunAJob, IntegrationPattern.WaitForCallback]
        self._integration_pattern = integration_pattern
        super(EcsRunTaskStep, self).__init__(state_id, "ecs:runTask", "Amazon ECS/AWS Fargate", **kwargs)
