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

# Test if boto3 session can fetch correct aws partition info from test environment

from stepfunctions.steps.utils import get_aws_partition, resource_integration_arn_builder
from stepfunctions.steps.integration_resources import IntegrationPattern, IntegrationServices, LambdaApi, SageMakerApi,\
                                            GlueApi, EcsApi, BatchApi, DynamoDBApi, SnsApi, SqsApi, ElasticMapReduceApi
import boto3
from unittest.mock import patch


@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_util_get_aws_partition_aws():
    cur_partition = get_aws_partition()
    assert cur_partition == "aws"


@patch.object(boto3.session.Session, 'region_name', 'cn-north-1')
def test_util_get_aws_partition_aws_cn():
    cur_partition = get_aws_partition()
    assert cur_partition == "aws-cn"


@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_arn_builder_lambda_no_wait():
    arn = resource_integration_arn_builder(IntegrationServices.Lambda, LambdaApi.Invoke)
    assert arn == "arn:aws:states:::lambda:invoke"


@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_arn_builder_lambda_wait_token():
    arn = resource_integration_arn_builder(IntegrationServices.Lambda, LambdaApi.Invoke,
                                           IntegrationPattern.WaitForTaskToken)
    assert arn == "arn:aws:states:::lambda:invoke.waitForTaskToken"


@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_arn_builder_sagemaker_no_wait():
    arn = resource_integration_arn_builder(IntegrationServices.SageMaker, SageMakerApi.CreateTrainingJob)
    assert arn == "arn:aws:states:::sagemaker:createTrainingJob"


@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_arn_builder_sagemaker_wait_completion():
    arn = resource_integration_arn_builder(IntegrationServices.SageMaker, SageMakerApi.CreateTrainingJob,
                                           IntegrationPattern.WaitForCompletion)
    assert arn == "arn:aws:states:::sagemaker:createTrainingJob.sync"


@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_arn_builder_glue_no_wait():
    arn = resource_integration_arn_builder(IntegrationServices.Glue, GlueApi.StartJobRun)
    assert arn == "arn:aws:states:::glue:startJobRun"


@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_arn_builder_glue_wait_completion():
    arn = resource_integration_arn_builder(IntegrationServices.Glue, GlueApi.StartJobRun,
                                           IntegrationPattern.WaitForCompletion)
    assert arn == "arn:aws:states:::glue:startJobRun.sync"


@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_arn_builder_ecs_no_wait():
    arn = resource_integration_arn_builder(IntegrationServices.ECS, EcsApi.RunTask)
    assert arn == "arn:aws:states:::ecs:runTask"


@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_arn_builder_ecs_wait_completion():
    arn = resource_integration_arn_builder(IntegrationServices.ECS, EcsApi.RunTask,
                                           IntegrationPattern.WaitForCompletion)
    assert arn == "arn:aws:states:::ecs:runTask.sync"


@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_arn_builder_batch_no_wait():
    arn = resource_integration_arn_builder(IntegrationServices.Batch, BatchApi.SubmitJob)
    assert arn == "arn:aws:states:::batch:submitJob"


@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_arn_builder_batch_wait_completion():
    arn = resource_integration_arn_builder(IntegrationServices.Batch, BatchApi.SubmitJob,
                                           IntegrationPattern.WaitForCompletion)
    assert arn == "arn:aws:states:::batch:submitJob.sync"


@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_arn_builder_dynamodb_no_wait():
    arn = resource_integration_arn_builder(IntegrationServices.DynamoDB, DynamoDBApi.GetItem)
    assert arn == "arn:aws:states:::dynamodb:getItem"


@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_arn_builder_sns_no_wait():
    arn = resource_integration_arn_builder(IntegrationServices.SNS, SnsApi.Publish)
    assert arn == "arn:aws:states:::sns:publish"


@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_arn_builder_sns_wait_token():
    arn = resource_integration_arn_builder(IntegrationServices.SNS, SnsApi.Publish,
                                           IntegrationPattern.WaitForTaskToken)
    assert arn == "arn:aws:states:::sns:publish.waitForTaskToken"


@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_arn_builder_sqs_no_wait():
    arn = resource_integration_arn_builder(IntegrationServices.SQS, SqsApi.SendMessage)
    assert arn == "arn:aws:states:::sqs:sendMessage"


@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_arn_builder_sqs_wait_token():
    arn = resource_integration_arn_builder(IntegrationServices.SQS, SqsApi.SendMessage,
                                           IntegrationPattern.WaitForTaskToken)
    assert arn == "arn:aws:states:::sqs:sendMessage.waitForTaskToken"


@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_arn_builder_elasticmapreduce_no_wait():
    arn = resource_integration_arn_builder(IntegrationServices.ElasticMapReduce, ElasticMapReduceApi.CreateCluster)
    assert arn == "arn:aws:states:::elasticmapreduce:createCluster"


@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_arn_builder_elasticmapreduce_wait_completion():
    arn = resource_integration_arn_builder(IntegrationServices.ElasticMapReduce, ElasticMapReduceApi.CreateCluster,
                                           IntegrationPattern.WaitForCompletion)
    assert arn == "arn:aws:states:::elasticmapreduce:createCluster.sync"

