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
EKS_SERVICES_NAME = "eks"
ELASTICMAPREDUCE_SERVICE_NAME = "elasticmapreduce"
EVENTBRIDGE_SERVICE_NAME = "events"
GLUE_DATABREW_SERVICE_NAME = "databrew"
SNS_SERVICE_NAME = "sns"
SQS_SERVICE_NAME = "sqs"
STEP_FUNCTIONS_SERVICE_NAME = "states"


class DynamoDBApi(Enum):
    GetItem = "getItem"
    PutItem = "putItem"
    DeleteItem = "deleteItem"
    UpdateItem = "updateItem"


class EksApi(Enum):
    CreateCluster = "createCluster"
    DeleteCluster = "deleteCluster"
    CreateFargateProfile = "createFargateProfile"
    DeleteFargateProfile = "deleteFargateProfile"
    CreateNodegroup = "createNodegroup"
    DeleteNodegroup = "deleteNodegroup"
    RunJob = "runJob"
    Call = "call"


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


class GlueDataBrewApi(Enum):
    StartJobRun = "startJobRun"


class SnsApi(Enum):
    Publish = "publish"


class SqsApi(Enum):
    SendMessage = "sendMessage"


class StepFunctions(Enum):
    StartExecution = "startExecution"


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


class EksCreateClusterStep(Task):
    """
    Creates a Task state that creates an Amazon EKS cluster. See `Call Amazon EKS with Step Functions <https://docs.aws.amazon.com/step-functions/latest/dg/connect-eks.html>`_ for more details.
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
            Example resource arn: arn:aws:states:::eks:createCluster.sync
            """

            kwargs[Field.Resource.value] = get_service_integration_arn(EKS_SERVICES_NAME,
                                                                       EksApi.CreateCluster,
                                                                       IntegrationPattern.WaitForCompletion)
        else:
            """
            Example resource arn: arn:aws:states:::eks:createCluster
            """

            kwargs[Field.Resource.value] = get_service_integration_arn(EKS_SERVICES_NAME,
                                                                       EksApi.CreateCluster)

        super(EksCreateClusterStep, self).__init__(state_id, **kwargs)


class EksCreateFargateProfileStep(Task):
    """
    Creates a Task state that creates an AWS Fargate profile for your Amazon EKS cluster. See `Call Amazon EKS with Step Functions <https://docs.aws.amazon.com/step-functions/latest/dg/connect-eks.html>`_ for more details.
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
            Example resource arn: arn:aws:states:::eks:createFargateProfile.sync
            """

            kwargs[Field.Resource.value] = get_service_integration_arn(EKS_SERVICES_NAME,
                                                                       EksApi.CreateFargateProfile,
                                                                       IntegrationPattern.WaitForCompletion)
        else:
            """
            Example resource arn: arn:aws:states:::eks:createFargateProfile
            """

            kwargs[Field.Resource.value] = get_service_integration_arn(EKS_SERVICES_NAME,
                                                                       EksApi.CreateFargateProfile)

        super(EksCreateFargateProfileStep, self).__init__(state_id, **kwargs)


class EksDeleteFargateProfileStep(Task):
    """
    Creates a Task state that deletes an AWS Fargate profile. See `Call Amazon EKS with Step Functions <https://docs.aws.amazon.com/step-functions/latest/dg/connect-eks.html>`_ for more details.
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
            Example resource arn: arn:aws:states:::eks:deleteFargateProfile.sync
            """

            kwargs[Field.Resource.value] = get_service_integration_arn(EKS_SERVICES_NAME,
                                                                       EksApi.DeleteFargateProfile,
                                                                       IntegrationPattern.WaitForCompletion)
        else:
            """
            Example resource arn: arn:aws:states:::eks:deleteFargateProfile
            """

            kwargs[Field.Resource.value] = get_service_integration_arn(EKS_SERVICES_NAME,
                                                                       EksApi.DeleteFargateProfile)

        super(EksDeleteFargateProfileStep, self).__init__(state_id, **kwargs)


class EksCreateNodeGroupStep(Task):
    """
    Creates a Task state that creates a node group for an Amazon EKS cluster. See `Call Amazon EKS with Step Functions <https://docs.aws.amazon.com/step-functions/latest/dg/connect-eks.html>`_ for more details.
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
            Example resource arn: arn:aws:states:::eks:createNodegroup.sync
            """

            kwargs[Field.Resource.value] = get_service_integration_arn(EKS_SERVICES_NAME,
                                                                       EksApi.CreateNodegroup,
                                                                       IntegrationPattern.WaitForCompletion)
        else:
            """
            Example resource arn: arn:aws:states:::eks:createNodegroup
            """

            kwargs[Field.Resource.value] = get_service_integration_arn(EKS_SERVICES_NAME,
                                                                       EksApi.CreateNodegroup)

        super(EksCreateNodeGroupStep, self).__init__(state_id, **kwargs)


class EksDeleteNodegroupStep(Task):
    """
    Creates a Task state that deletes an Amazon EKS node group for a cluster. See `Call Amazon EKS with Step Functions <https://docs.aws.amazon.com/step-functions/latest/dg/connect-eks.html>`_ for more details.
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
            Example resource arn: arn:aws:states:::eks:deleteNodegroup.sync
            """

            kwargs[Field.Resource.value] = get_service_integration_arn(EKS_SERVICES_NAME,
                                                                       EksApi.DeleteNodegroup,
                                                                       IntegrationPattern.WaitForCompletion)
        else:
            """
            Example resource arn: arn:aws:states:::eks:deleteNodegroup
            """

            kwargs[Field.Resource.value] = get_service_integration_arn(EKS_SERVICES_NAME,
                                                                       EksApi.DeleteNodegroup)

        super(EksDeleteNodegroupStep, self).__init__(state_id, **kwargs)


class EksDeleteClusterStep(Task):
    """
    Creates a Task state that deletes an Amazon EKS cluster. See `Call Amazon EKS with Step Functions <https://docs.aws.amazon.com/step-functions/latest/dg/connect-eks.html>`_ for more details.
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
            Example resource arn: arn:aws:states:::eks:deleteCluster.sync
            """

            kwargs[Field.Resource.value] = get_service_integration_arn(EKS_SERVICES_NAME,
                                                                       EksApi.DeleteCluster,
                                                                       IntegrationPattern.WaitForCompletion)
        else:
            """
            Example resource arn: arn:aws:states:::eks:deleteCluster
            """

            kwargs[Field.Resource.value] = get_service_integration_arn(EKS_SERVICES_NAME,
                                                                       EksApi.DeleteCluster)

        super(EksDeleteClusterStep, self).__init__(state_id, **kwargs)


class EksRunJobStep(Task):
    """
    Creates a Task state that allows you to run a job on your Amazon EKS cluster. See `Call Amazon EKS with Step Functions <https://docs.aws.amazon.com/step-functions/latest/dg/connect-eks.html>`_ for more details.
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
            Example resource arn: arn:aws:states:::eks:runJob.sync
            """

            kwargs[Field.Resource.value] = get_service_integration_arn(EKS_SERVICES_NAME,
                                                                       EksApi.RunJob,
                                                                       IntegrationPattern.WaitForCompletion)
        else:
            """
            Example resource arn: arn:aws:states:::eks:runJob
            """

            kwargs[Field.Resource.value] = get_service_integration_arn(EKS_SERVICES_NAME,
                                                                       EksApi.RunJob)

        super(EksRunJobStep, self).__init__(state_id, **kwargs)


class EksCallStep(Task):
    """
    Creates a Task state that allows you to use the Kubernetes API to read and write Kubernetes resource objects via a Kubernetes API endpoint. See `Call Amazon EKS with Step Functions <https://docs.aws.amazon.com/step-functions/latest/dg/connect-eks.html>`_ for more details.
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
        Example resource arn: arn:aws:states:::eks:call
        """

        kwargs[Field.Resource.value] = get_service_integration_arn(EKS_SERVICES_NAME,
                                                                   EksApi.Call)

        super(EksCallStep, self).__init__(state_id, **kwargs)


class GlueDataBrewStartJobRunStep(Task):

    """
    Creates a Task state that starts a DataBrew job. See `Manage AWS Glue DataBrew Jobs with Step Functions <https://docs.aws.amazon.com/step-functions/latest/dg/connect-databrew.html>`_ for more details.
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
            Example resource arn: arn:aws:states:::databrew:startJobRun.sync
            """

            kwargs[Field.Resource.value] = get_service_integration_arn(GLUE_DATABREW_SERVICE_NAME,
                                                                       GlueDataBrewApi.StartJobRun,
                                                                       IntegrationPattern.WaitForCompletion)
        else:
            """
            Example resource arn: arn:aws:states:::databrew:startJobRun
            """

            kwargs[Field.Resource.value] = get_service_integration_arn(GLUE_DATABREW_SERVICE_NAME,
                                                                       GlueDataBrewApi.StartJobRun)

        super(GlueDataBrewStartJobRunStep, self).__init__(state_id, **kwargs)


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


class StepFunctionsStartExecutionStep(Task):

    """
    Creates a Task state that starts an execution of another state machine. See `Manage AWS Step Functions Executions as an Integrated Service <https://docs.aws.amazon.com/step-functions/latest/dg/connect-stepfunctions.html`_ for more details.

    Property flags: There are three flags (wait_for_callback, wait_for_completion and async_call) that can be set in order to select which Step Functions resource to use.
        One of three must be enabled to create the step successfully.
    """

    def __init__(self, state_id, wait_for_callback=False, wait_for_completion=True, async_call=False, **kwargs):
        """
        Args:
            state_id (str): State name whose length **must be** less than or equal to 128 unicode characters. State names **must be** unique within the scope of the whole state machine.
            wait_for_callback(bool, optional): Boolean value set to `True` if the Task state should wait for callback to resume the operation. (default: False)
            wait_for_completion (bool, optional): Boolean value set to `True` if the Task state should wait to complete before proceeding to the next step in the workflow. (default: True)
            async_call(bool, optional): Boolean value set to `True` for the Task proceed to the next step in the workflow without waiting for completion. (default: False):
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
        # Validate that only 1 one of the property flags are set to true
        property_flags = [(wait_for_callback, "wait_for_callback"), (wait_for_completion, "wait_for_completion"),
                          (async_call, "async_call")]
        enabled_property_flags = [property_flag[1] for property_flag in property_flags if property_flag[0]]
        if not enabled_property_flags:
            raise ValueError(f"No resource flag enabled - Please enable one of "
                             f"{[property_flag[1] for property_flag in property_flags]}")
        elif len(enabled_property_flags) > 1:
            raise ValueError(f"Multiple resource flags enabled({enabled_property_flags}) - "
                             f"Please enable only one.")

        if wait_for_callback:
            """
            Example resource arn: arn:aws:states:::states:startExecution.waitForTaskToken
            """

            kwargs[Field.Resource.value] = get_service_integration_arn(STEP_FUNCTIONS_SERVICE_NAME,
                                                                       StepFunctions.StartExecution,
                                                                       IntegrationPattern.WaitForTaskToken)
        elif wait_for_completion:
                """
                Example resource arn:aws:states:::states:startExecution.sync:2
                """

                kwargs[Field.Resource.value] = get_service_integration_arn(STEP_FUNCTIONS_SERVICE_NAME,
                                                                           StepFunctions.StartExecution,
                                                                           IntegrationPattern.WaitForCompletionWithJsonResponse)
        else:
            """
            Example resource arn:aws:states:::states:startExecution
            """
            kwargs[Field.Resource.value] = get_service_integration_arn(STEP_FUNCTIONS_SERVICE_NAME,
                                                                       StepFunctions.StartExecution)

        super(StepFunctionsStartExecutionStep, self).__init__(state_id, **kwargs)
