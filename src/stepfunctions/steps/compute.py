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

from stepfunctions.steps.states import Task
from stepfunctions.steps.fields import Field


class LambdaStep(Task):

    """
    Creates a Task state to invoke an AWS Lambda function. See `Invoke Lambda with Step Functions <https://docs.aws.amazon.com/step-functions/latest/dg/connect-lambda.html>`_ for more details.
    """

    def __init__(self, state_id, wait_for_callback=False, **kwargs):
        """
        Args:
            state_id (str): State name whose length **must be** less than or equal to 128 unicode characters. State names **must be** unique within the scope of the whole state machine.
            wait_for_callback(bool, optional): Boolean value set to `True` if the Task state should wait for callback to resume the operation. (default: False)
            timeout_seconds (int, optional): Positive integer specifying timeout for the state in seconds. If the state runs longer than the specified timeout, then the interpreter fails the state with a `States.Timeout` Error Name. (default: 60)
            timeout_seconds_path (str, optional): Path specifying the state's timeout value in seconds from the state input. When resolved, the path must select a field whose value is a positive integer.
            heartbeat_seconds (int, optional): Positive integer specifying heartbeat timeout for the state in seconds. This value should be lower than the one specified for `timeout_seconds`. If more time than the specified heartbeat elapses between heartbeats from the task, then the interpreter fails the state with a `States.Timeout` Error Name.
            heartbeat_seconds_path (str, optional): Path specifying the state's heartbeat value in seconds from the state input. When resolved, the path must select a field whose value is a positive integer.
            comment (str, optional): Human-readable comment or description. (default: None)
            input_path (str, optional): Path applied to the state’s raw input to select some or all of it; that selection is used by the state. (default: '$')
            parameters (dict, optional): The value of this field becomes the effective input for the state.
            result_path (str, optional): Path specifying the raw input’s combination with or replacement by the state’s result. (default: '$')
            output_path (str, optional): Path applied to the state’s output after the application of `result_path`, producing the effective output which serves as the raw input for the next state. (default: '$')
        """
        if wait_for_callback:
            kwargs[Field.Resource.value] = 'arn:aws:states:::lambda:invoke.waitForTaskToken'
        else:
            kwargs[Field.Resource.value] = 'arn:aws:states:::lambda:invoke'

        super(LambdaStep, self).__init__(state_id, **kwargs)


class GlueStartJobRunStep(Task):

    """
    Creates a Task state to run an AWS Glue job. See `Manage AWS Glue Jobs with Step Functions <https://docs.aws.amazon.com/step-functions/latest/dg/connect-glue.html>`_ for more details.
    """

    def __init__(self, state_id, wait_for_completion=True, **kwargs):
        """
        Args:
            state_id (str): State name whose length **must be** less than or equal to 128 unicode characters. State names **must be** unique within the scope of the whole state machine.
            wait_for_completion(bool, optional): Boolean value set to `True` if the Task state should wait for the glue job to complete before proceeding to the next step in the workflow. Set to `False` if the Task state should submit the glue job and proceed to the next step. (default: True)
            timeout_seconds (int, optional): Positive integer specifying timeout for the state in seconds. If the state runs longer than the specified timeout, then the interpreter fails the state with a `States.Timeout` Error Name. (default: 60)
            timeout_seconds_path (str, optional): Path specifying the state's timeout value in seconds from the state input. When resolved, the path must select a field whose value is a positive integer.
            heartbeat_seconds (int, optional): Positive integer specifying heartbeat timeout for the state in seconds. This value should be lower than the one specified for `timeout_seconds`. If more time than the specified heartbeat elapses between heartbeats from the task, then the interpreter fails the state with a `States.Timeout` Error Name.
            heartbeat_seconds_path (str, optional): Path specifying the state's heartbeat value in seconds from the state input. When resolved, the path must select a field whose value is a positive integer.
            comment (str, optional): Human-readable comment or description. (default: None)
            input_path (str, optional): Path applied to the state’s raw input to select some or all of it; that selection is used by the state. (default: '$')
            parameters (dict, optional): The value of this field becomes the effective input for the state.
            result_path (str, optional): Path specifying the raw input’s combination with or replacement by the state’s result. (default: '$')
            output_path (str, optional): Path applied to the state’s output after the application of `result_path`, producing the effective output which serves as the raw input for the next state. (default: '$')
        """
        if wait_for_completion:
            kwargs[Field.Resource.value] = 'arn:aws:states:::glue:startJobRun.sync'
        else:
            kwargs[Field.Resource.value] = 'arn:aws:states:::glue:startJobRun'

        super(GlueStartJobRunStep, self).__init__(state_id, **kwargs)


class BatchSubmitJobStep(Task):

    """
    Creates a Task State to start an AWS Batch job. See `Manage AWS Batch with Step Functions <https://docs.aws.amazon.com/step-functions/latest/dg/connect-batch.html>`_ for more details.
    """

    def __init__(self, state_id, wait_for_completion=True, **kwargs):
        """
        Args:
            state_id (str): State name whose length **must be** less than or equal to 128 unicode characters. State names **must be** unique within the scope of the whole state machine.
            wait_for_completion(bool, optional): Boolean value set to `True` if the Task state should wait for the batch job to complete before proceeding to the next step in the workflow. Set to `False` if the Task state should submit the batch job and proceed to the next step. (default: True)
            timeout_seconds (int, optional): Positive integer specifying timeout for the state in seconds. If the state runs longer than the specified timeout, then the interpreter fails the state with a `States.Timeout` Error Name. (default: 60)
            timeout_seconds_path (str, optional): Path specifying the state's timeout value in seconds from the state input. When resolved, the path must select a field whose value is a positive integer.
            heartbeat_seconds (int, optional): Positive integer specifying heartbeat timeout for the state in seconds. This value should be lower than the one specified for `timeout_seconds`. If more time than the specified heartbeat elapses between heartbeats from the task, then the interpreter fails the state with a `States.Timeout` Error Name.
            heartbeat_seconds_path (str, optional): Path specifying the state's heartbeat value in seconds from the state input. When resolved, the path must select a field whose value is a positive integer.
            comment (str, optional): Human-readable comment or description. (default: None)
            input_path (str, optional): Path applied to the state’s raw input to select some or all of it; that selection is used by the state. (default: '$')
            parameters (dict, optional): The value of this field becomes the effective input for the state.
            result_path (str, optional): Path specifying the raw input’s combination with or replacement by the state’s result. (default: '$')
            output_path (str, optional): Path applied to the state’s output after the application of `result_path`, producing the effective output which serves as the raw input for the next state. (default: '$')
        """
        if wait_for_completion:
            kwargs[Field.Resource.value] = 'arn:aws:states:::batch:submitJob.sync'
        else:
            kwargs[Field.Resource.value] = 'arn:aws:states:::batch:submitJob'

        super(BatchSubmitJobStep, self).__init__(state_id, **kwargs)


class EcsRunTaskStep(Task):

    """
    Creates a Task State to run Amazon ECS or Fargate Tasks. See `Manage Amazon ECS or Fargate Tasks with Step Functions <https://docs.aws.amazon.com/step-functions/latest/dg/connect-ecs.html>`_ for more details.
    """

    def __init__(self, state_id, wait_for_completion=True, **kwargs):
        """
        Args:
            state_id (str): State name whose length **must be** less than or equal to 128 unicode characters. State names **must be** unique within the scope of the whole state machine.
            wait_for_completion(bool, optional): Boolean value set to `True` if the Task state should wait for the ecs job to complete before proceeding to the next step in the workflow. Set to `False` if the Task state should submit the ecs job and proceed to the next step. (default: True)
            timeout_seconds (int, optional): Positive integer specifying timeout for the state in seconds. If the state runs longer than the specified timeout, then the interpreter fails the state with a `States.Timeout` Error Name. (default: 60)
            timeout_seconds_path (str, optional): Path specifying the state's timeout value in seconds from the state input. When resolved, the path must select a field whose value is a positive integer.
            heartbeat_seconds (int, optional): Positive integer specifying heartbeat timeout for the state in seconds. This value should be lower than the one specified for `timeout_seconds`. If more time than the specified heartbeat elapses between heartbeats from the task, then the interpreter fails the state with a `States.Timeout` Error Name.
            heartbeat_seconds_path (str, optional): Path specifying the state's heartbeat value in seconds from the state input. When resolved, the path must select a field whose value is a positive integer.
            comment (str, optional): Human-readable comment or description. (default: None)
            input_path (str, optional): Path applied to the state’s raw input to select some or all of it; that selection is used by the state. (default: '$')
            parameters (dict, optional): The value of this field becomes the effective input for the state.
            result_path (str, optional): Path specifying the raw input’s combination with or replacement by the state’s result. (default: '$')
            output_path (str, optional): Path applied to the state’s output after the application of `result_path`, producing the effective output which serves as the raw input for the next state. (default: '$')
        """
        if wait_for_completion:
            kwargs[Field.Resource.value] = 'arn:aws:states:::ecs:runTask.sync'
        else:
            kwargs[Field.Resource.value] = 'arn:aws:states:::ecs:runTask'

        super(EcsRunTaskStep, self).__init__(state_id, **kwargs)
