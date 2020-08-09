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


from stepfunctions.steps.fields import Field
from stepfunctions.steps.states import Task, IntegrationPattern


class DynamoDBGetItemStep(Task):
    """
    Creates a Task state to get an item from DynamoDB. See `Call DynamoDB APIs with Step Functions <https://docs.aws.amazon.com/step-functions/latest/dg/connect-ddb.html>`_ for more details.
    """

    def __init__(self, state_id, **kwargs):
        """
        Args:
            state_id (str): State name whose length **must be** less than or equal to 128 unicode characters. State names **must be** unique within the scope of the whole state machine.
            comment (str, optional): Human-readable comment or description. (default: None)
            input_path (str, optional): Path applied to the state’s raw input to select some or all of it; that selection is used by the state. (default: '$')
            parameters (dict, optional): The value of this field becomes the effective input for the state.
            result_path (str, optional): Path specifying the raw input’s combination with or replacement by the state’s result. (default: '$')
            output_path (str, optional): Path applied to the state’s output after the application of `result_path`, producing the effective output which serves as the raw input for the next state. (default: '$')
        """
        kwargs[Field.Resource.value] = 'arn:aws:states:::dynamodb:getItem'
        super(DynamoDBGetItemStep, self).__init__(state_id, 'dynamodb:getItem',
                                                  'DynamoDB', **kwargs)


class DynamoDBPutItemStep(Task):
    """
    Creates a Task state to put an item to DynamoDB. See `Call DynamoDB APIs with Step Functions <https://docs.aws.amazon.com/step-functions/latest/dg/connect-ddb.html>`_ for more details.
    """

    def __init__(self, state_id, **kwargs):
        """
        Args:
            state_id (str): State name whose length **must be** less than or equal to 128 unicode characters. State names **must be** unique within the scope of the whole state machine.
            comment (str, optional): Human-readable comment or description. (default: None)
            input_path (str, optional): Path applied to the state’s raw input to select some or all of it; that selection is used by the state. (default: '$')
            parameters (dict, optional): The value of this field becomes the effective input for the state.
            result_path (str, optional): Path specifying the raw input’s combination with or replacement by the state’s result. (default: '$')
            output_path (str, optional): Path applied to the state’s output after the application of `result_path`, producing the effective output which serves as the raw input for the next state. (default: '$')
        """
        super(DynamoDBPutItemStep, self).__init__(state_id, 'dynamodb:putItem',
                                                  'DynamoDB', **kwargs)


class DynamoDBDeleteItemStep(Task):
    """
    Creates a Task state to delete an item from DynamoDB. See `Call DynamoDB APIs with Step Functions <https://docs.aws.amazon.com/step-functions/latest/dg/connect-ddb.html>`_ for more details.
    """

    def __init__(self, state_id, **kwargs):
        """
        Args:
            state_id (str): State name whose length **must be** less than or equal to 128 unicode characters. State names **must be** unique within the scope of the whole state machine.
            comment (str, optional): Human-readable comment or description. (default: None)
            input_path (str, optional): Path applied to the state’s raw input to select some or all of it; that selection is used by the state. (default: '$')
            parameters (dict, optional): The value of this field becomes the effective input for the state.
            result_path (str, optional): Path specifying the raw input’s combination with or replacement by the state’s result. (default: '$')
            output_path (str, optional): Path applied to the state’s output after the application of `result_path`, producing the effective output which serves as the raw input for the next state. (default: '$')
        """
        super(DynamoDBDeleteItemStep, self).__init__(state_id, 'dynamodb:deleteItem',
                                                     'DynamoDB', **kwargs)


class DynamoDBUpdateItemStep(Task):
    """
    Creates a Task state to update an item from DynamoDB. See `Call DynamoDB APIs with Step Functions <https://docs.aws.amazon.com/step-functions/latest/dg/connect-ddb.html>`_ for more details.
    """

    def __init__(self, state_id, **kwargs):
        """
        Args:
            state_id (str): State name whose length **must be** less than or equal to 128 unicode characters. State names **must be** unique within the scope of the whole state machine.
            comment (str, optional): Human-readable comment or description. (default: None)
            input_path (str, optional): Path applied to the state’s raw input to select some or all of it; that selection is used by the state. (default: '$')
            parameters (dict, optional): The value of this field becomes the effective input for the state.
            result_path (str, optional): Path specifying the raw input’s combination with or replacement by the state’s result. (default: '$')
            output_path (str, optional): Path applied to the state’s output after the application of `result_path`, producing the effective output which serves as the raw input for the next state. (default: '$')
        """
        super(DynamoDBUpdateItemStep, self).__init__(state_id, 'dynamodb:updateItem',
                                                     'DynamoDB', **kwargs)


class SnsPublishStep(Task):
    """
    Creates a Task state to publish a message to SNS topic. See `Call Amazon SNS with Step Functions <https://docs.aws.amazon.com/step-functions/latest/dg/connect-sns.html>`_ for more details.
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
        super(SnsPublishStep, self).__init__(state_id, 'sns:publish', 'Amazon SNS', **kwargs)


class SqsSendMessageStep(Task):
    """
    Creates a Task state to send a message to SQS queue. See `Call Amazon SQS with Step Functions <https://docs.aws.amazon.com/step-functions/latest/dg/connect-sqs.html>`_ for more details.
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
        super(SqsSendMessageStep, self).__init__(state_id, 'sqs:sendMessage',
                                                 'Amazon SQS', **kwargs)


class EmrCreateClusterStep(Task):
    """
    Creates a Task state to create and start running a cluster (job flow). See `Call Amazon EMR with Step Functions <https://docs.aws.amazon.com/step-functions/latest/dg/connect-emr.html>`_ for more details.
    """

    def __init__(self, state_id, integration_pattern=IntegrationPattern.RunAJob, **kwargs):
        """
        Args:
            state_id (str): State name whose length **must be** less than or equal to 128 unicode characters. State names **must be** unique within the scope of the whole state machine.
            comment (str, optional): Human-readable comment or description. (default: None)
            input_path (str, optional): Path applied to the state’s raw input to select some or all of it; that selection is used by the state. (default: '$')
            parameters (dict, optional): The value of this field becomes the effective input for the state.
            result_path (str, optional): Path specifying the raw input’s combination with or replacement by the state’s result. (default: '$')
            output_path (str, optional): Path applied to the state’s output after the application of `result_path`, producing the effective output which serves as the raw input for the next state. (default: '$')
            integration_pattern(stepfunctions.states.IntegrationPattern, optional): Enum value set to RunAJob if the task should wait to complete before proceeding to the next step in the workflow, set to WaitForCallback if the Task state should wait for callback to resume the operation or set to RequestResponse if the Task should wait for HTTP response (default: RequestResponse)
        """
        self._valid_patterns = [IntegrationPattern.RequestResponse, IntegrationPattern.RunAJob]
        self._integration_pattern = integration_pattern
        super(EmrCreateClusterStep, self).__init__(state_id, 'elasticmapreduce:createCluster',
                                                   'Amazon EMR', **kwargs)


class EmrTerminateClusterStep(Task):
    """
    Creates a Task state to shut down a cluster (job flow). See `Call Amazon EMR with Step Functions <https://docs.aws.amazon.com/step-functions/latest/dg/connect-emr.html>`_ for more details.
    """

    def __init__(self, state_id, integration_pattern=IntegrationPattern.RunAJob, **kwargs):
        """
        Args:
            state_id (str): State name whose length **must be** less than or equal to 128 unicode characters. State names **must be** unique within the scope of the whole state machine.
            comment (str, optional): Human-readable comment or description. (default: None)
            input_path (str, optional): Path applied to the state’s raw input to select some or all of it; that selection is used by the state. (default: '$')
            parameters (dict, optional): The value of this field becomes the effective input for the state.
            result_path (str, optional): Path specifying the raw input’s combination with or replacement by the state’s result. (default: '$')
            output_path (str, optional): Path applied to the state’s output after the application of `result_path`, producing the effective output which serves as the raw input for the next state. (default: '$')
            integration_pattern(stepfunctions.states.IntegrationPattern, optional): Enum value set to RunAJob if the task should wait to complete before proceeding to the next step in the workflow, set to WaitForCallback if the Task state should wait for callback to resume the operation or set to RequestResponse if the Task should wait for HTTP response (default: RequestResponse)
        """
        self._valid_patterns = [IntegrationPattern.RequestResponse, IntegrationPattern.RunAJob]
        self._integration_pattern = integration_pattern
        super(EmrTerminateClusterStep, self).__init__(state_id, 'elasticmapreduce:terminateCluster',
                                                      'Amazon EMR', **kwargs)


class EmrAddStepStep(Task):
    """
    Creates a Task state to add a new step to a running cluster. See `Call Amazon EMR with Step Functions <https://docs.aws.amazon.com/step-functions/latest/dg/connect-emr.html>`_ for more details.
    """

    def __init__(self, state_id, integration_pattern=IntegrationPattern.RunAJob, **kwargs):
        """
        Args:
            state_id (str): State name whose length **must be** less than or equal to 128 unicode characters. State names **must be** unique within the scope of the whole state machine.
            comment (str, optional): Human-readable comment or description. (default: None)
            input_path (str, optional): Path applied to the state’s raw input to select some or all of it; that selection is used by the state. (default: '$')
            parameters (dict, optional): The value of this field becomes the effective input for the state.
            result_path (str, optional): Path specifying the raw input’s combination with or replacement by the state’s result. (default: '$')
            output_path (str, optional): Path applied to the state’s output after the application of `result_path`, producing the effective output which serves as the raw input for the next state. (default: '$')
            integration_pattern(stepfunctions.states.IntegrationPattern, optional): Enum value set to RunAJob if the task should wait to complete before proceeding to the next step in the workflow, set to WaitForCallback if the Task state should wait for callback to resume the operation or set to RequestResponse if the Task should wait for HTTP response (default: RequestResponse)
        """
        self._valid_patterns = [IntegrationPattern.RequestResponse, IntegrationPattern.RunAJob]
        self._integration_pattern = integration_pattern
        super(EmrAddStepStep, self).__init__(state_id, 'elasticmapreduce:addStep',
                                             'Amazon EMR', **kwargs)


class EmrCancelStepStep(Task):
    """
    Creates a Task state to cancel a pending step in a running cluster. See `Call Amazon EMR with Step Functions <https://docs.aws.amazon.com/step-functions/latest/dg/connect-emr.html>`_ for more details.
    """

    def __init__(self, state_id, **kwargs):
        """
        Args:
            state_id (str): State name whose length **must be** less than or equal to 128 unicode characters. State names **must be** unique within the scope of the whole state machine.
            comment (str, optional): Human-readable comment or description. (default: None)
            input_path (str, optional): Path applied to the state’s raw input to select some or all of it; that selection is used by the state. (default: '$')
            parameters (dict, optional): The value of this field becomes the effective input for the state.
            result_path (str, optional): Path specifying the raw input’s combination with or replacement by the state’s result. (default: '$')
            output_path (str, optional): Path applied to the state’s output after the application of `result_path`, producing the effective output which serves as the raw input for the next state. (default: '$')
        """
        super(EmrCancelStepStep, self).__init__(state_id, 'elasticmapreduce:cancelStep',
                                                'Amazon EMR', **kwargs)


class EmrSetClusterTerminationProtectionStep(Task):
    """
    Creates a Task state to lock a cluster (job flow) so the EC2 instances in the cluster cannot be terminated by user intervention, an API call, or a job-flow error. See `Call Amazon EMR with Step Functions <https://docs.aws.amazon.com/step-functions/latest/dg/connect-emr.html>`_ for more details.
    """

    def __init__(self, state_id, **kwargs):
        """
        Args:
            state_id (str): State name whose length **must be** less than or equal to 128 unicode characters. State names **must be** unique within the scope of the whole state machine.
            comment (str, optional): Human-readable comment or description. (default: None)
            input_path (str, optional): Path applied to the state’s raw input to select some or all of it; that selection is used by the state. (default: '$')
            parameters (dict, optional): The value of this field becomes the effective input for the state.
            result_path (str, optional): Path specifying the raw input’s combination with or replacement by the state’s result. (default: '$')
            output_path (str, optional): Path applied to the state’s output after the application of `result_path`, producing the effective output which serves as the raw input for the next state. (default: '$')
        """
        super(EmrSetClusterTerminationProtectionStep, self).__init__(state_id,
                                                                     'elasticmapreduce:setClusterTerminationProtection',
                                                                     'Amazon EMR', **kwargs)


class EmrModifyInstanceFleetByNameStep(Task):
    """
    Creates a Task state to modify the target On-Demand and target Spot capacities for an instance fleet.  See `Call Amazon EMR with Step Functions <https://docs.aws.amazon.com/step-functions/latest/dg/connect-emr.html>`_ for more details.
    """

    def __init__(self, state_id, **kwargs):
        """
        Args:
            state_id (str): State name whose length **must be** less than or equal to 128 unicode characters. State names **must be** unique within the scope of the whole state machine.
            comment (str, optional): Human-readable comment or description. (default: None)
            input_path (str, optional): Path applied to the state’s raw input to select some or all of it; that selection is used by the state. (default: '$')
            parameters (dict, optional): The value of this field becomes the effective input for the state.
            result_path (str, optional): Path specifying the raw input’s combination with or replacement by the state’s result. (default: '$')
            output_path (str, optional): Path applied to the state’s output after the application of `result_path`, producing the effective output which serves as the raw input for the next state. (default: '$')
        """
        super(EmrModifyInstanceFleetByNameStep, self).__init__(state_id, 'elasticmapreduce:modifyInstanceFleetByName',
                                                               'Amazon EMR', **kwargs)


class EmrModifyInstanceGroupByNameStep(Task):
    """
    Creates a Task state to modify the number of nodes and configuration settings of an instance group. See `Call Amazon EMR with Step Functions <https://docs.aws.amazon.com/step-functions/latest/dg/connect-emr.html>`_ for more details.
    """

    def __init__(self, state_id, **kwargs):
        """
        Args:
            state_id (str): State name whose length **must be** less than or equal to 128 unicode characters. State names **must be** unique within the scope of the whole state machine.
            comment (str, optional): Human-readable comment or description. (default: None)
            input_path (str, optional): Path applied to the state’s raw input to select some or all of it; that selection is used by the state. (default: '$')
            parameters (dict, optional): The value of this field becomes the effective input for the state.
            result_path (str, optional): Path specifying the raw input’s combination with or replacement by the state’s result. (default: '$')
            output_path (str, optional): Path applied to the state’s output after the application of `result_path`, producing the effective output which serves as the raw input for the next state. (default: '$')
        """
        super(EmrModifyInstanceGroupByNameStep, self).__init__(state_id, 'elasticmapreduce:modifyInstanceGroupByName',
                                                               'Amazon EMR', **kwargs)
