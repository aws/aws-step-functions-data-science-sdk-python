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

from enum import Enum
from stepfunctions.steps.states import Task
from stepfunctions.steps.fields import Field
from stepfunctions.steps.integration_resources import IntegrationPattern, get_service_integration_arn

DYNAMODB_SERVICE_NAME = "dynamodb"
ELASTICMAPREDUCE_SERVICE_NAME = "elasticmapreduce"
EVENTBRIDGE_SERVICE_NAME = "events"
SNS_SERVICE_NAME = "sns"
SQS_SERVICE_NAME = "sqs"



class DynamoDBApi(Enum):
    GetItem = "getItem"
    PutItem = "putItem"
    DeleteItem = "deleteItem"
    UpdateItem = "updateItem"


class SnsApi(Enum):
    Publish = "publish"


class SqsApi(Enum):
    SendMessage = "sendMessage"


class ElasticMapReduceApi(Enum):
    CreateCluster = "createCluster"
    TerminateCluster = "terminateCluster"
    AddStep = "addStep"
    CancelStep = "cancelStep"
    SetClusterTerminationProtection = "setClusterTerminationProtection"
    ModifyInstanceFleetByName = "modifyInstanceFleetByName"
    ModifyInstanceGroupByName = "modifyInstanceGroupByName"


class EventBridgeApi(Enum):
    PutEvents = "putEvents"


class DynamoDBGetItemStep(Task):
    """
    Creates a Task state to get an item from DynamoDB. See `Call DynamoDB APIs with Step Functions <https://docs.aws.amazon.com/step-functions/latest/dg/connect-ddb.html>`_ for more details.
    """

    def __init__(self, state_id, **kwargs):
        """
        Args:
            state_id (str): State name whose length **must be** less than or equal to 128 unicode characters. State names **must be** unique within the scope of the whole state machine.
            comment (str, optional): Human-readable comment or description. (default: None)
            timeout_seconds (int, optional): Positive integer specifying timeout for the state in seconds. If the state runs longer than the specified timeout, then the interpreter fails the state with a `States.Timeout` Error Name. (default: 60)
            timeout_seconds_path (str, optional): Path specifying the state's timeout value in seconds from the state input. When resolved, the path must select a field whose value is a positive integer.
            heartbeat_seconds (int, optional): Positive integer specifying heartbeat timeout for the state in seconds. This value should be lower than the one specified for `timeout_seconds`. If more time than the specified heartbeat elapses between heartbeats from the task, then the interpreter fails the state with a `States.Timeout` Error Name.
            heartbeat_seconds_path (str, optional): Path specifying the state's heartbeat value in seconds from the state input. When resolved, the path must select a field whose value is a positive integer.
            input_path (str, optional): Path applied to the state’s raw input to select some or all of it; that selection is used by the state. (default: '$')
            parameters (dict, optional): The value of this field becomes the effective input for the state.
            result_path (str, optional): Path specifying the raw input’s combination with or replacement by the state’s result. (default: '$')
            output_path (str, optional): Path applied to the state’s output after the application of `result_path`, producing the effective output which serves as the raw input for the next state. (default: '$')
        """

        """
        Example resource arn: arn:aws:states:::dynamodb:getItem
        """

        kwargs[Field.Resource.value] = get_service_integration_arn(DYNAMODB_SERVICE_NAME,
                                                                   DynamoDBApi.GetItem)
        super(DynamoDBGetItemStep, self).__init__(state_id, **kwargs)


class EventBridgePutEventsStep(Task):

    """
    Creates a Task to send custom events to Amazon EventBridge. See`Call EventBridge with Step Functions <https://docs.aws.amazon.com/step-functions/latest/dg/connect-eventbridge.html>`_ for more details.
    """

    def __init__(self, state_id, wait_for_callback=False, **kwargs):
        """
        Args:
            state_id (str): State name whose length **must be** less than or equal to 128 unicode characters. State names **must be** unique within the scope of the whole state machine.
            comment (str, optional): Human-readable comment or description. (default: None)
            timeout_seconds (int, optional): Positive integer specifying timeout for the state in seconds. If the state runs longer than the specified timeout, then the interpreter fails the state with a `States.Timeout` Error Name. (default: 60)
            timeout_seconds_path (str, optional): Path specifying the state's timeout value in seconds from the state input. When resolved, the path must select a field whose value is a positive integer.
            heartbeat_seconds (int, optional): Positive integer specifying heartbeat timeout for the state in seconds. This value should be lower than the one specified for `timeout_seconds`. If more time than the specified heartbeat elapses between heartbeats from the task, then the interpreter fails the state with a `States.Timeout` Error Name.
            heartbeat_seconds_path (str, optional): Path specifying the state's heartbeat value in seconds from the state input. When resolved, the path must select a field whose value is a positive integer.
            input_path (str, optional): Path applied to the state’s raw input to select some or all of it; that selection is used by the state. (default: '$')
            parameters (dict, optional): The value of this field becomes the effective input for the state.
            result_path (str, optional): Path specifying the raw input’s combination with or replacement by the state’s result. (default: '$')
            output_path (str, optional): Path applied to the state’s output after the application of `result_path`, producing the effective output which serves as the raw input for the next state. (default: '$')
        """

        if wait_for_callback:
            """
            Example resource arn: arn:aws:states:::events:putEvents.waitForTaskToken
            """

            kwargs[Field.Resource.value] = get_service_integration_arn(EVENTBRIDGE_SERVICE_NAME,
                                                                       EventBridgeApi.PutEvents,
                                                                       IntegrationPattern.WaitForTaskToken)
        else:
            """
            Example resource arn: arn:aws:states:::events:putEvents
            """

            kwargs[Field.Resource.value] = get_service_integration_arn(EVENTBRIDGE_SERVICE_NAME,
                                                                       EventBridgeApi.PutEvents)

        super(EventBridgePutEventsStep, self).__init__(state_id, **kwargs)


class DynamoDBPutItemStep(Task):

    """
    Creates a Task state to put an item to DynamoDB. See `Call DynamoDB APIs with Step Functions <https://docs.aws.amazon.com/step-functions/latest/dg/connect-ddb.html>`_ for more details.
    """

    def __init__(self, state_id, **kwargs):
        """
        Args:
            state_id (str): State name whose length **must be** less than or equal to 128 unicode characters. State names **must be** unique within the scope of the whole state machine.
            comment (str, optional): Human-readable comment or description. (default: None)
            timeout_seconds (int, optional): Positive integer specifying timeout for the state in seconds. If the state runs longer than the specified timeout, then the interpreter fails the state with a `States.Timeout` Error Name. (default: 60)
            timeout_seconds_path (str, optional): Path specifying the state's timeout value in seconds from the state input. When resolved, the path must select a field whose value is a positive integer.
            heartbeat_seconds (int, optional): Positive integer specifying heartbeat timeout for the state in seconds. This value should be lower than the one specified for `timeout_seconds`. If more time than the specified heartbeat elapses between heartbeats from the task, then the interpreter fails the state with a `States.Timeout` Error Name.
            heartbeat_seconds_path (str, optional): Path specifying the state's heartbeat value in seconds from the state input. When resolved, the path must select a field whose value is a positive integer.
            input_path (str, optional): Path applied to the state’s raw input to select some or all of it; that selection is used by the state. (default: '$')
            parameters (dict, optional): The value of this field becomes the effective input for the state.
            result_path (str, optional): Path specifying the raw input’s combination with or replacement by the state’s result. (default: '$')
            output_path (str, optional): Path applied to the state’s output after the application of `result_path`, producing the effective output which serves as the raw input for the next state. (default: '$')
        """

        """
        Example resource arn: arn:aws:states:::dynamodb:putItem
        """

        kwargs[Field.Resource.value] = get_service_integration_arn(DYNAMODB_SERVICE_NAME,
                                                                   DynamoDBApi.PutItem)
        super(DynamoDBPutItemStep, self).__init__(state_id, **kwargs)


class DynamoDBDeleteItemStep(Task):

    """
    Creates a Task state to delete an item from DynamoDB. See `Call DynamoDB APIs with Step Functions <https://docs.aws.amazon.com/step-functions/latest/dg/connect-ddb.html>`_ for more details.
    """

    def __init__(self, state_id, **kwargs):
        """
        Args:
            state_id (str): State name whose length **must be** less than or equal to 128 unicode characters. State names **must be** unique within the scope of the whole state machine.
            comment (str, optional): Human-readable comment or description. (default: None)
            timeout_seconds (int, optional): Positive integer specifying timeout for the state in seconds. If the state runs longer than the specified timeout, then the interpreter fails the state with a `States.Timeout` Error Name. (default: 60)
            timeout_seconds_path (str, optional): Path specifying the state's timeout value in seconds from the state input. When resolved, the path must select a field whose value is a positive integer.
            heartbeat_seconds (int, optional): Positive integer specifying heartbeat timeout for the state in seconds. This value should be lower than the one specified for `timeout_seconds`. If more time than the specified heartbeat elapses between heartbeats from the task, then the interpreter fails the state with a `States.Timeout` Error Name.
            heartbeat_seconds_path (str, optional): Path specifying the state's heartbeat value in seconds from the state input. When resolved, the path must select a field whose value is a positive integer.
            input_path (str, optional): Path applied to the state’s raw input to select some or all of it; that selection is used by the state. (default: '$')
            parameters (dict, optional): The value of this field becomes the effective input for the state.
            result_path (str, optional): Path specifying the raw input’s combination with or replacement by the state’s result. (default: '$')
            output_path (str, optional): Path applied to the state’s output after the application of `result_path`, producing the effective output which serves as the raw input for the next state. (default: '$')
        """

        """
        Example resource arn: arn:aws:states:::dynamodb:deleteItem
        """

        kwargs[Field.Resource.value] = get_service_integration_arn(DYNAMODB_SERVICE_NAME,
                                                                   DynamoDBApi.DeleteItem)
        super(DynamoDBDeleteItemStep, self).__init__(state_id, **kwargs)


class DynamoDBUpdateItemStep(Task):

    """
    Creates a Task state to update an item from DynamoDB. See `Call DynamoDB APIs with Step Functions <https://docs.aws.amazon.com/step-functions/latest/dg/connect-ddb.html>`_ for more details.
    """

    def __init__(self, state_id, **kwargs):
        """
        Args:
            state_id (str): State name whose length **must be** less than or equal to 128 unicode characters. State names **must be** unique within the scope of the whole state machine.
            comment (str, optional): Human-readable comment or description. (default: None)
            timeout_seconds (int, optional): Positive integer specifying timeout for the state in seconds. If the state runs longer than the specified timeout, then the interpreter fails the state with a `States.Timeout` Error Name. (default: 60)
            timeout_seconds_path (str, optional): Path specifying the state's timeout value in seconds from the state input. When resolved, the path must select a field whose value is a positive integer.
            heartbeat_seconds (int, optional): Positive integer specifying heartbeat timeout for the state in seconds. This value should be lower than the one specified for `timeout_seconds`. If more time than the specified heartbeat elapses between heartbeats from the task, then the interpreter fails the state with a `States.Timeout` Error Name.
            heartbeat_seconds_path (str, optional): Path specifying the state's heartbeat value in seconds from the state input. When resolved, the path must select a field whose value is a positive integer.
            input_path (str, optional): Path applied to the state’s raw input to select some or all of it; that selection is used by the state. (default: '$')
            parameters (dict, optional): The value of this field becomes the effective input for the state.
            result_path (str, optional): Path specifying the raw input’s combination with or replacement by the state’s result. (default: '$')
            output_path (str, optional): Path applied to the state’s output after the application of `result_path`, producing the effective output which serves as the raw input for the next state. (default: '$')
        """

        """
        Example resource arn: arn:aws:states:::dynamodb:updateItem
        """

        kwargs[Field.Resource.value] = get_service_integration_arn(DYNAMODB_SERVICE_NAME,
                                                                   DynamoDBApi.UpdateItem)
        super(DynamoDBUpdateItemStep, self).__init__(state_id, **kwargs)


class SnsPublishStep(Task):

    """
    Creates a Task state to publish a message to SNS topic. See `Call Amazon SNS with Step Functions <https://docs.aws.amazon.com/step-functions/latest/dg/connect-sns.html>`_ for more details.
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
            """
            Example resource arn: arn:aws:states:::sns:publish.waitForTaskToken
            """

            kwargs[Field.Resource.value] = get_service_integration_arn(SNS_SERVICE_NAME,
                                                                       SnsApi.Publish,
                                                                       IntegrationPattern.WaitForTaskToken)
        else:
            """
            Example resource arn: arn:aws:states:::sns:publish
            """

            kwargs[Field.Resource.value] = get_service_integration_arn(SNS_SERVICE_NAME,
                                                                       SnsApi.Publish)

        super(SnsPublishStep, self).__init__(state_id, **kwargs)


class SqsSendMessageStep(Task):

    """
    Creates a Task state to send a message to SQS queue. See `Call Amazon SQS with Step Functions <https://docs.aws.amazon.com/step-functions/latest/dg/connect-sqs.html>`_ for more details.
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
            """
            Example resource arn: arn:aws:states:::sqs:sendMessage.waitForTaskToken
            """

            kwargs[Field.Resource.value] =  get_service_integration_arn(SQS_SERVICE_NAME,
                                                                        SqsApi.SendMessage,
                                                                        IntegrationPattern.WaitForTaskToken)
        else:
            """
            Example resource arn: arn:aws:states:::sqs:sendMessage
            """

            kwargs[Field.Resource.value] = get_service_integration_arn(SQS_SERVICE_NAME,
                                                                       SqsApi.SendMessage)

        super(SqsSendMessageStep, self).__init__(state_id, **kwargs)


class EmrCreateClusterStep(Task):
    """
    Creates a Task state to create and start running a cluster (job flow). See `Call Amazon EMR with Step Functions <https://docs.aws.amazon.com/step-functions/latest/dg/connect-emr.html>`_ for more details.
    """

    def __init__(self, state_id, wait_for_completion=True, **kwargs):
        """
        Args:
            state_id (str): State name whose length **must be** less than or equal to 128 unicode characters. State names **must be** unique within the scope of the whole state machine.
            comment (str, optional): Human-readable comment or description. (default: None)
            timeout_seconds (int, optional): Positive integer specifying timeout for the state in seconds. If the state runs longer than the specified timeout, then the interpreter fails the state with a `States.Timeout` Error Name. (default: 60)
            timeout_seconds_path (str, optional): Path specifying the state's timeout value in seconds from the state input. When resolved, the path must select a field whose value is a positive integer.
            heartbeat_seconds (int, optional): Positive integer specifying heartbeat timeout for the state in seconds. This value should be lower than the one specified for `timeout_seconds`. If more time than the specified heartbeat elapses between heartbeats from the task, then the interpreter fails the state with a `States.Timeout` Error Name.
            heartbeat_seconds_path (str, optional): Path specifying the state's heartbeat value in seconds from the state input. When resolved, the path must select a field whose value is a positive integer.
            input_path (str, optional): Path applied to the state’s raw input to select some or all of it; that selection is used by the state. (default: '$')
            parameters (dict, optional): The value of this field becomes the effective input for the state.
            result_path (str, optional): Path specifying the raw input’s combination with or replacement by the state’s result. (default: '$')
            output_path (str, optional): Path applied to the state’s output after the application of `result_path`, producing the effective output which serves as the raw input for the next state. (default: '$')
            wait_for_completion (bool, optional): Boolean value set to `True` if the Task state should wait to complete before proceeding to the next step in the workflow. (default: True)
        """
        if wait_for_completion:
            """
            Example resource arn: arn:aws:states:::elasticmapreduce:createCluster.sync
            """

            kwargs[Field.Resource.value] = get_service_integration_arn(ELASTICMAPREDUCE_SERVICE_NAME,
                                                                       ElasticMapReduceApi.CreateCluster,
                                                                       IntegrationPattern.WaitForCompletion)
        else:
            """
            Example resource arn: arn:aws:states:::elasticmapreduce:createCluster
            """

            kwargs[Field.Resource.value] = get_service_integration_arn(ELASTICMAPREDUCE_SERVICE_NAME,
                                                                       ElasticMapReduceApi.CreateCluster)

        super(EmrCreateClusterStep, self).__init__(state_id, **kwargs)


class EmrTerminateClusterStep(Task):
    """
    Creates a Task state to shut down a cluster (job flow). See `Call Amazon EMR with Step Functions <https://docs.aws.amazon.com/step-functions/latest/dg/connect-emr.html>`_ for more details.
    """

    def __init__(self, state_id, wait_for_completion=True, **kwargs):
        """
        Args:
            state_id (str): State name whose length **must be** less than or equal to 128 unicode characters. State names **must be** unique within the scope of the whole state machine.
            comment (str, optional): Human-readable comment or description. (default: None)
            timeout_seconds (int, optional): Positive integer specifying timeout for the state in seconds. If the state runs longer than the specified timeout, then the interpreter fails the state with a `States.Timeout` Error Name. (default: 60)
            timeout_seconds_path (str, optional): Path specifying the state's timeout value in seconds from the state input. When resolved, the path must select a field whose value is a positive integer.
            heartbeat_seconds (int, optional): Positive integer specifying heartbeat timeout for the state in seconds. This value should be lower than the one specified for `timeout_seconds`. If more time than the specified heartbeat elapses between heartbeats from the task, then the interpreter fails the state with a `States.Timeout` Error Name.
            heartbeat_seconds_path (str, optional): Path specifying the state's heartbeat value in seconds from the state input. When resolved, the path must select a field whose value is a positive integer.
            input_path (str, optional): Path applied to the state’s raw input to select some or all of it; that selection is used by the state. (default: '$')
            parameters (dict, optional): The value of this field becomes the effective input for the state.
            result_path (str, optional): Path specifying the raw input’s combination with or replacement by the state’s result. (default: '$')
            output_path (str, optional): Path applied to the state’s output after the application of `result_path`, producing the effective output which serves as the raw input for the next state. (default: '$')
            wait_for_completion (bool, optional): Boolean value set to `True` if the Task state should wait to complete before proceeding to the next step in the workflow. (default: True)
        """
        if wait_for_completion:
            """
            Example resource arn: arn:aws:states:::elasticmapreduce:terminateCluster.sync
            """

            kwargs[Field.Resource.value] = get_service_integration_arn(ELASTICMAPREDUCE_SERVICE_NAME,
                                                                       ElasticMapReduceApi.TerminateCluster,
                                                                       IntegrationPattern.WaitForCompletion)
        else:
            """
            Example resource arn: arn:aws:states:::elasticmapreduce:terminateCluster
            """

            kwargs[Field.Resource.value] = get_service_integration_arn(ELASTICMAPREDUCE_SERVICE_NAME,
                                                                       ElasticMapReduceApi.TerminateCluster)

        super(EmrTerminateClusterStep, self).__init__(state_id, **kwargs)


class EmrAddStepStep(Task):
    """
    Creates a Task state to add a new step to a running cluster. See `Call Amazon EMR with Step Functions <https://docs.aws.amazon.com/step-functions/latest/dg/connect-emr.html>`_ for more details.
    """

    def __init__(self, state_id, wait_for_completion=True, **kwargs):
        """
        Args:
            state_id (str): State name whose length **must be** less than or equal to 128 unicode characters. State names **must be** unique within the scope of the whole state machine.
            comment (str, optional): Human-readable comment or description. (default: None)
            timeout_seconds (int, optional): Positive integer specifying timeout for the state in seconds. If the state runs longer than the specified timeout, then the interpreter fails the state with a `States.Timeout` Error Name. (default: 60)
            timeout_seconds_path (str, optional): Path specifying the state's timeout value in seconds from the state input. When resolved, the path must select a field whose value is a positive integer.
            heartbeat_seconds (int, optional): Positive integer specifying heartbeat timeout for the state in seconds. This value should be lower than the one specified for `timeout_seconds`. If more time than the specified heartbeat elapses between heartbeats from the task, then the interpreter fails the state with a `States.Timeout` Error Name.
            heartbeat_seconds_path (str, optional): Path specifying the state's heartbeat value in seconds from the state input. When resolved, the path must select a field whose value is a positive integer.
            input_path (str, optional): Path applied to the state’s raw input to select some or all of it; that selection is used by the state. (default: '$')
            parameters (dict, optional): The value of this field becomes the effective input for the state.
            result_path (str, optional): Path specifying the raw input’s combination with or replacement by the state’s result. (default: '$')
            output_path (str, optional): Path applied to the state’s output after the application of `result_path`, producing the effective output which serves as the raw input for the next state. (default: '$')
            wait_for_completion (bool, optional): Boolean value set to `True` if the Task state should wait to complete before proceeding to the next step in the workflow. (default: True)
        """
        if wait_for_completion:
            """
            Example resource arn: arn:aws:states:::elasticmapreduce:addStep.sync
            """

            kwargs[Field.Resource.value] = get_service_integration_arn(ELASTICMAPREDUCE_SERVICE_NAME,
                                                                       ElasticMapReduceApi.AddStep,
                                                                       IntegrationPattern.WaitForCompletion)
        else:
            """
            Example resource arn: arn:aws:states:::elasticmapreduce:addStep
            """

            kwargs[Field.Resource.value] = get_service_integration_arn(ELASTICMAPREDUCE_SERVICE_NAME,
                                                                       ElasticMapReduceApi.AddStep)

        super(EmrAddStepStep, self).__init__(state_id, **kwargs)


class EmrCancelStepStep(Task):
    """
    Creates a Task state to cancel a pending step in a running cluster. See `Call Amazon EMR with Step Functions <https://docs.aws.amazon.com/step-functions/latest/dg/connect-emr.html>`_ for more details.
    """

    def __init__(self, state_id, **kwargs):
        """
        Args:
            state_id (str): State name whose length **must be** less than or equal to 128 unicode characters. State names **must be** unique within the scope of the whole state machine.
            comment (str, optional): Human-readable comment or description. (default: None)
            timeout_seconds (int, optional): Positive integer specifying timeout for the state in seconds. If the state runs longer than the specified timeout, then the interpreter fails the state with a `States.Timeout` Error Name. (default: 60)
            timeout_seconds_path (str, optional): Path specifying the state's timeout value in seconds from the state input. When resolved, the path must select a field whose value is a positive integer.
            heartbeat_seconds (int, optional): Positive integer specifying heartbeat timeout for the state in seconds. This value should be lower than the one specified for `timeout_seconds`. If more time than the specified heartbeat elapses between heartbeats from the task, then the interpreter fails the state with a `States.Timeout` Error Name.
            heartbeat_seconds_path (str, optional): Path specifying the state's heartbeat value in seconds from the state input. When resolved, the path must select a field whose value is a positive integer.
            input_path (str, optional): Path applied to the state’s raw input to select some or all of it; that selection is used by the state. (default: '$')
            parameters (dict, optional): The value of this field becomes the effective input for the state.
            result_path (str, optional): Path specifying the raw input’s combination with or replacement by the state’s result. (default: '$')
            output_path (str, optional): Path applied to the state’s output after the application of `result_path`, producing the effective output which serves as the raw input for the next state. (default: '$')
        """

        """
        Example resource arn: arn:aws:states:::elasticmapreduce:cancelStep
        """

        kwargs[Field.Resource.value] = get_service_integration_arn(ELASTICMAPREDUCE_SERVICE_NAME,
                                                                   ElasticMapReduceApi.CancelStep)

        super(EmrCancelStepStep, self).__init__(state_id, **kwargs)


class EmrSetClusterTerminationProtectionStep(Task):
    """
    Creates a Task state to lock a cluster (job flow) so the EC2 instances in the cluster cannot be terminated by user intervention, an API call, or a job-flow error. See `Call Amazon EMR with Step Functions <https://docs.aws.amazon.com/step-functions/latest/dg/connect-emr.html>`_ for more details.
    """

    def __init__(self, state_id, **kwargs):
        """
        Args:
            state_id (str): State name whose length **must be** less than or equal to 128 unicode characters. State names **must be** unique within the scope of the whole state machine.
            comment (str, optional): Human-readable comment or description. (default: None)
            timeout_seconds (int, optional): Positive integer specifying timeout for the state in seconds. If the state runs longer than the specified timeout, then the interpreter fails the state with a `States.Timeout` Error Name. (default: 60)
            timeout_seconds_path (str, optional): Path specifying the state's timeout value in seconds from the state input. When resolved, the path must select a field whose value is a positive integer.
            heartbeat_seconds (int, optional): Positive integer specifying heartbeat timeout for the state in seconds. This value should be lower than the one specified for `timeout_seconds`. If more time than the specified heartbeat elapses between heartbeats from the task, then the interpreter fails the state with a `States.Timeout` Error Name.
            heartbeat_seconds_path (str, optional): Path specifying the state's heartbeat value in seconds from the state input. When resolved, the path must select a field whose value is a positive integer.
            input_path (str, optional): Path applied to the state’s raw input to select some or all of it; that selection is used by the state. (default: '$')
            parameters (dict, optional): The value of this field becomes the effective input for the state.
            result_path (str, optional): Path specifying the raw input’s combination with or replacement by the state’s result. (default: '$')
            output_path (str, optional): Path applied to the state’s output after the application of `result_path`, producing the effective output which serves as the raw input for the next state. (default: '$')
        """

        """
        Example resource arn: arn:aws:states:::elasticmapreduce:setClusterTerminationProtection
        """

        kwargs[Field.Resource.value] = get_service_integration_arn(ELASTICMAPREDUCE_SERVICE_NAME,
                                                                   ElasticMapReduceApi.SetClusterTerminationProtection)

        super(EmrSetClusterTerminationProtectionStep, self).__init__(state_id, **kwargs)


class EmrModifyInstanceFleetByNameStep(Task):
    """
    Creates a Task state to modify the target On-Demand and target Spot capacities for an instance fleet.  See `Call Amazon EMR with Step Functions <https://docs.aws.amazon.com/step-functions/latest/dg/connect-emr.html>`_ for more details.
    """

    def __init__(self, state_id, **kwargs):
        """
        Args:
            state_id (str): State name whose length **must be** less than or equal to 128 unicode characters. State names **must be** unique within the scope of the whole state machine.
            comment (str, optional): Human-readable comment or description. (default: None)
            timeout_seconds (int, optional): Positive integer specifying timeout for the state in seconds. If the state runs longer than the specified timeout, then the interpreter fails the state with a `States.Timeout` Error Name. (default: 60)
            timeout_seconds_path (str, optional): Path specifying the state's timeout value in seconds from the state input. When resolved, the path must select a field whose value is a positive integer.
            heartbeat_seconds (int, optional): Positive integer specifying heartbeat timeout for the state in seconds. This value should be lower than the one specified for `timeout_seconds`. If more time than the specified heartbeat elapses between heartbeats from the task, then the interpreter fails the state with a `States.Timeout` Error Name.
            heartbeat_seconds_path (str, optional): Path specifying the state's heartbeat value in seconds from the state input. When resolved, the path must select a field whose value is a positive integer.
            input_path (str, optional): Path applied to the state’s raw input to select some or all of it; that selection is used by the state. (default: '$')
            parameters (dict, optional): The value of this field becomes the effective input for the state.
            result_path (str, optional): Path specifying the raw input’s combination with or replacement by the state’s result. (default: '$')
            output_path (str, optional): Path applied to the state’s output after the application of `result_path`, producing the effective output which serves as the raw input for the next state. (default: '$')
        """

        """
        Example resource arn: arn:aws:states:::elasticmapreduce:modifyInstanceFleetByName
        """

        kwargs[Field.Resource.value] = get_service_integration_arn(ELASTICMAPREDUCE_SERVICE_NAME,
                                                                   ElasticMapReduceApi.ModifyInstanceFleetByName)

        super(EmrModifyInstanceFleetByNameStep, self).__init__(state_id, **kwargs)


class EmrModifyInstanceGroupByNameStep(Task):
    """
    Creates a Task state to modify the number of nodes and configuration settings of an instance group. See `Call Amazon EMR with Step Functions <https://docs.aws.amazon.com/step-functions/latest/dg/connect-emr.html>`_ for more details.
    """

    def __init__(self, state_id, **kwargs):
        """
        Args:
            state_id (str): State name whose length **must be** less than or equal to 128 unicode characters. State names **must be** unique within the scope of the whole state machine.
            comment (str, optional): Human-readable comment or description. (default: None)
            timeout_seconds (int, optional): Positive integer specifying timeout for the state in seconds. If the state runs longer than the specified timeout, then the interpreter fails the state with a `States.Timeout` Error Name. (default: 60)
            timeout_seconds_path (str, optional): Path specifying the state's timeout value in seconds from the state input. When resolved, the path must select a field whose value is a positive integer.
            heartbeat_seconds (int, optional): Positive integer specifying heartbeat timeout for the state in seconds. This value should be lower than the one specified for `timeout_seconds`. If more time than the specified heartbeat elapses between heartbeats from the task, then the interpreter fails the state with a `States.Timeout` Error Name.
            heartbeat_seconds_path (str, optional): Path specifying the state's heartbeat value in seconds from the state input. When resolved, the path must select a field whose value is a positive integer.
            input_path (str, optional): Path applied to the state’s raw input to select some or all of it; that selection is used by the state. (default: '$')
            parameters (dict, optional): The value of this field becomes the effective input for the state.
            result_path (str, optional): Path specifying the raw input’s combination with or replacement by the state’s result. (default: '$')
            output_path (str, optional): Path applied to the state’s output after the application of `result_path`, producing the effective output which serves as the raw input for the next state. (default: '$')
        """

        """
        Example resource arn: arn:aws:states:::elasticmapreduce:modifyInstanceGroupByName
        """

        kwargs[Field.Resource.value] = get_service_integration_arn(ELASTICMAPREDUCE_SERVICE_NAME,
                                                                   ElasticMapReduceApi.ModifyInstanceGroupByName)

        super(EmrModifyInstanceGroupByNameStep, self).__init__(state_id, **kwargs)
