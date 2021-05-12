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

"""
Enum classes for task integration resource arn builder
"""


class IntegrationPattern(Enum):
    WaitForTaskToken = "waitForTaskToken"
    WaitForCompletion = "sync"


class IntegrationServices(Enum):
    Lambda = "lambda"
    SageMaker = "sagemaker"
    Glue = "glue"
    ECS = "ecs"
    Batch = "batch"
    DynamoDB = "dynamodb"
    SNS = "sns"
    SQS = "sqs"
    ElasticMapReduce = "elasticmapreduce"


class LambdaApi(Enum):
    Invoke = "invoke"


class SageMakerApi(Enum):
    CreateTrainingJob = "createTrainingJob"
    CreateTransformJob = "createTransformJob"
    CreateModel = "createModel"
    CreateEndpointConfig = "createEndpointConfig"
    UpdateEndpoint = "updateEndpoint"
    CreateEndpoint = "createEndpoint"
    CreateHyperParameterTuningJob = "createHyperParameterTuningJob"
    CreateProcessingJob = "createProcessingJob"


class GlueApi(Enum):
    StartJobRun = "startJobRun"


class EcsApi(Enum):
    RunTask = "runTask"


class BatchApi(Enum):
    SubmitJob = "submitJob"


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
