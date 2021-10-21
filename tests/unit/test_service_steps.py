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
from stepfunctions.steps.service import DynamoDBGetItemStep, DynamoDBPutItemStep, DynamoDBUpdateItemStep, DynamoDBDeleteItemStep
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
from stepfunctions.steps.service import EmrCreateClusterStep, EmrTerminateClusterStep, EmrAddStepStep, EmrCancelStepStep, EmrSetClusterTerminationProtectionStep, EmrModifyInstanceFleetByNameStep, EmrModifyInstanceGroupByNameStep
from stepfunctions.steps.service import EventBridgePutEventsStep
from stepfunctions.steps.service import SnsPublishStep, SqsSendMessageStep
from stepfunctions.steps.service import GlueDataBrewStartJobRunStep
from stepfunctions.steps.service import StepFunctionsStartExecutionStep
from stepfunctions.steps.integration_resources import IntegrationPattern


@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_sns_publish_step_creation():
    step = SnsPublishStep('Publish to SNS', parameters={
        'TopicArn': 'arn:aws:sns:us-east-1:123456789012:myTopic',
        'Message': 'message',
    })

    assert step.to_dict() == {
        'Type': 'Task',
        'Resource': 'arn:aws:states:::sns:publish',
        'Parameters': {
            'TopicArn': 'arn:aws:sns:us-east-1:123456789012:myTopic',
            'Message': 'message',
        },
        'End': True
    }

    step = SnsPublishStep('Publish to SNS', wait_for_callback=True, parameters={
        'TopicArn': 'arn:aws:sns:us-east-1:123456789012:myTopic',
        'Message': {
            'Input.$': '$',
            'TaskToken.$': '$$.Task.Token'
        }
    })

    assert step.to_dict() == {
        'Type': 'Task',
        'Resource': 'arn:aws:states:::sns:publish.waitForTaskToken',
        'Parameters': {
            'TopicArn': 'arn:aws:sns:us-east-1:123456789012:myTopic',
            'Message': {
                'Input.$': '$',
                'TaskToken.$': '$$.Task.Token'
            }
        },
        'End': True
    }


@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_sqs_send_message_step_creation():
    step = SqsSendMessageStep('Send to SQS', parameters={
        'QueueUrl': 'https://sqs.us-east-1.amazonaws.com/123456789012/myQueue',
        'MessageBody': 'Hello'
    })

    assert step.to_dict() == {
        'Type': 'Task',
        'Resource': 'arn:aws:states:::sqs:sendMessage',
        'Parameters': {
            'QueueUrl': 'https://sqs.us-east-1.amazonaws.com/123456789012/myQueue',
            'MessageBody': 'Hello'
        },
        'End': True
    }

    step = SqsSendMessageStep('Send to SQS', wait_for_callback=True, parameters={
        'QueueUrl': 'https://sqs.us-east-1.amazonaws.com/123456789012/myQueue',
        'MessageBody': {
            'Input.$': '$',
            'TaskToken.$': '$$.Task.Token'
        }
    })

    assert step.to_dict() == {
        'Type': 'Task',
        'Resource': 'arn:aws:states:::sqs:sendMessage.waitForTaskToken',
        'Parameters': {
            'QueueUrl': 'https://sqs.us-east-1.amazonaws.com/123456789012/myQueue',
            'MessageBody': {
                'Input.$': '$',
                'TaskToken.$': '$$.Task.Token'
            }
        },
        'End': True
    }

@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_eventbridge_put_events_step_creation():
    step = EventBridgePutEventsStep('Send to EventBridge', parameters={
        "Entries": [
            {
                "Detail": {
                    "Message": "MyMessage"
                },
                "DetailType": "MyDetailType",
                "EventBusName": "MyEventBus",
                "Source": "my.source"
            }
        ]
    })

    assert step.to_dict() == {
        "Type": "Task",
        "Resource": 'arn:aws:states:::events:putEvents',
        "Parameters": {
            "Entries": [
                {
                    "Detail": {
                        "Message": "MyMessage"
                    },
                    "DetailType": "MyDetailType",
                    "EventBusName": "MyEventBus",
                    "Source": "my.source"
                }
            ]
        },
        "End": True
    }

    step = EventBridgePutEventsStep('Send to EventBridge', wait_for_callback=True, parameters={
        "Entries": [
            {
                "Detail": {
                    "Message.$": "$.MyMessage"
                },
                "DetailType": "MyDetailType",
                "EventBusName": "MyEventBus",
                "Source": "my.source"
            }
        ]
    })

    assert step.to_dict() == {
        "Type": "Task",
        "Resource": "arn:aws:states:::events:putEvents.waitForTaskToken",
        "Parameters": {
            "Entries": [
                {
                    "Detail": {
                        "Message.$": "$.MyMessage"
                    },
                    "DetailType": "MyDetailType",
                    "EventBusName": "MyEventBus",
                    "Source": "my.source"
                }
            ]
        },
        "End": True
    }


@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_dynamodb_get_item_step_creation():
    step = DynamoDBGetItemStep('Read Message From DynamoDB', parameters={
        'TableName': 'TransferDataRecords-DDBTable-3I41R5L5EAGT',
        'Key': {
            'MessageId': {
                'S.$': '$.List[0]'
            }
        }
    })

    assert step.to_dict() == {
        'Type': 'Task',
        'Resource': 'arn:aws:states:::dynamodb:getItem',
        'Parameters': {
            'TableName': 'TransferDataRecords-DDBTable-3I41R5L5EAGT',
            'Key': {
                'MessageId': {
                    'S.$': '$.List[0]'
                }
            }
        },
        'End': True
    }


@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_dynamodb_put_item_step_creation():
    step = DynamoDBPutItemStep('Add Message From DynamoDB', parameters={
        'TableName': 'TransferDataRecords-DDBTable-3I41R5L5EAGT',
        'Item': {
            'MessageId': {
                'S': '123456789'
            }
        }
    })

    assert step.to_dict() == {
        'Type': 'Task',
        'Resource': 'arn:aws:states:::dynamodb:putItem',
        'Parameters': {
            'TableName': 'TransferDataRecords-DDBTable-3I41R5L5EAGT',
            'Item': {
                'MessageId': {
                    'S': '123456789'
                }
            }
        },
        'End': True
    }


@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_dynamodb_delete_item_step_creation():
    step = DynamoDBDeleteItemStep('Delete Message From DynamoDB', parameters={
        'TableName': 'TransferDataRecords-DDBTable-3I41R5L5EAGT',
        'Key': {
            'MessageId': {
                'S': 'MyMessage'
            }
        }
    })

    assert step.to_dict() == {
        'Type': 'Task',
        'Resource': 'arn:aws:states:::dynamodb:deleteItem',
        'Parameters': {
            'TableName': 'TransferDataRecords-DDBTable-3I41R5L5EAGT',
            'Key': {
                'MessageId': {
                    'S': 'MyMessage'
                }
            }
        },
        'End': True
    }


@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_dynamodb_update_item_step_creation():
    step = DynamoDBUpdateItemStep('Update Message From DynamoDB', parameters={
        'TableName': 'TransferDataRecords-DDBTable-3I41R5L5EAGT',
        'Key': {
            'RecordId': {
                'S': 'RecordId'
            }
        },
        'UpdateExpression': 'set Revision = :val1',
        'ExpressionAttributeValues': {
            ':val1': { 'S': '2' }
        }
    })

    assert step.to_dict() == {
        'Type': 'Task',
        'Resource': 'arn:aws:states:::dynamodb:updateItem',
        'Parameters': {
            'TableName': 'TransferDataRecords-DDBTable-3I41R5L5EAGT',
            'Key': {
                'RecordId': {
                    'S': 'RecordId'
                }
            },
            'UpdateExpression': 'set Revision = :val1',
            'ExpressionAttributeValues': {
                ':val1': { 'S': '2' }
            }
        },
        'End': True
    }


@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_emr_create_cluster_step_creation():
    step = EmrCreateClusterStep('Create EMR cluster', parameters={
        'Name': 'MyWorkflowCluster',
        'VisibleToAllUsers': True,
        'ReleaseLabel': 'emr-5.28.0',
        'Applications': [
            {
                'Name': 'Hive'
            }
        ],
        'ServiceRole': 'EMR_DefaultRole',
        'JobFlowRole': 'EMR_EC2_DefaultRole',
        'LogUri': 's3n://aws-logs-123456789012-us-east-1/elasticmapreduce/',
        'Instances': {
            'KeepJobFlowAliveWhenNoSteps': True,
            'InstanceFleets': [
                {
                    'InstanceFleetType': 'MASTER',
                    'Name': 'MASTER',   
                    'TargetOnDemandCapacity': 1,
                    'InstanceTypeConfigs': [
                        {
                            'InstanceType': 'm4.xlarge'
                        }
                    ]
                },
                {
                    'InstanceFleetType': 'CORE',
                    'Name': 'CORE',
                    'TargetOnDemandCapacity': 1,
                    'InstanceTypeConfigs': [
                        {
                            'InstanceType': 'm4.xlarge'
                        }
                    ]
                }
            ]
        }
    })

    assert step.to_dict() == {
        'Type': 'Task',
        'Resource': 'arn:aws:states:::elasticmapreduce:createCluster.sync',
        'Parameters': {
            'Name': 'MyWorkflowCluster',
            'VisibleToAllUsers': True,
            'ReleaseLabel': 'emr-5.28.0',
            'Applications': [
                {
                    'Name': 'Hive'
                }
            ],
            'ServiceRole': 'EMR_DefaultRole',
            'JobFlowRole': 'EMR_EC2_DefaultRole',
            'LogUri': 's3n://aws-logs-123456789012-us-east-1/elasticmapreduce/',
            'Instances': {
                'KeepJobFlowAliveWhenNoSteps': True,
                'InstanceFleets': [
                    {
                        'InstanceFleetType': 'MASTER',
                        'Name': 'MASTER',   
                        'TargetOnDemandCapacity': 1,
                        'InstanceTypeConfigs': [
                            {
                                'InstanceType': 'm4.xlarge'
                            }
                        ]
                    },
                    {
                        'InstanceFleetType': 'CORE',
                        'Name': 'CORE',
                        'TargetOnDemandCapacity': 1,
                        'InstanceTypeConfigs': [
                            {
                                'InstanceType': 'm4.xlarge'
                            }
                        ]
                    }
                ]
            }
        },
        'End': True
    }

    step = EmrCreateClusterStep('Create EMR cluster', wait_for_completion=False, parameters={
        'Name': 'MyWorkflowCluster',
        'VisibleToAllUsers': True,
        'ReleaseLabel': 'emr-5.28.0',
        'Applications': [
            {
                'Name': 'Hive'
            }
        ],
        'ServiceRole': 'EMR_DefaultRole',
        'JobFlowRole': 'EMR_EC2_DefaultRole',
        'LogUri': 's3n://aws-logs-123456789012-us-east-1/elasticmapreduce/',
        'Instances': {
            'KeepJobFlowAliveWhenNoSteps': True,
            'InstanceFleets': [
                {
                    'InstanceFleetType': 'MASTER',
                    'Name': 'MASTER',   
                    'TargetOnDemandCapacity': 1,
                    'InstanceTypeConfigs': [
                        {
                            'InstanceType': 'm4.xlarge'
                        }
                    ]
                },
                {
                    'InstanceFleetType': 'CORE',
                    'Name': 'CORE',
                    'TargetOnDemandCapacity': 1,
                    'InstanceTypeConfigs': [
                        {
                            'InstanceType': 'm4.xlarge'
                        }
                    ]
                }
            ]
        }
    })


    assert step.to_dict() == {
        'Type': 'Task',
        'Resource': 'arn:aws:states:::elasticmapreduce:createCluster',
        'Parameters': {
            'Name': 'MyWorkflowCluster',
            'VisibleToAllUsers': True,
            'ReleaseLabel': 'emr-5.28.0',
            'Applications': [
                {
                    'Name': 'Hive'
                }
            ],
            'ServiceRole': 'EMR_DefaultRole',
            'JobFlowRole': 'EMR_EC2_DefaultRole',
            'LogUri': 's3n://aws-logs-123456789012-us-east-1/elasticmapreduce/',
            'Instances': {
                'KeepJobFlowAliveWhenNoSteps': True,
                'InstanceFleets': [
                    {
                        'InstanceFleetType': 'MASTER',
                        'Name': 'MASTER',   
                        'TargetOnDemandCapacity': 1,
                        'InstanceTypeConfigs': [
                            {
                                'InstanceType': 'm4.xlarge'
                            }
                        ]
                    },
                    {
                        'InstanceFleetType': 'CORE',
                        'Name': 'CORE',
                        'TargetOnDemandCapacity': 1,
                        'InstanceTypeConfigs': [
                            {
                                'InstanceType': 'm4.xlarge'
                            }
                        ]
                    }
                ]
            }
        },
        'End': True
    }


@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_emr_terminate_cluster_step_creation():
    step = EmrTerminateClusterStep('Terminate EMR cluster', parameters={
        'ClusterId': 'MyWorkflowClusterId'
    })

    assert step.to_dict() == {
        'Type': 'Task',
        'Resource': 'arn:aws:states:::elasticmapreduce:terminateCluster.sync',
        'Parameters': {
            'ClusterId': 'MyWorkflowClusterId',
        },
        'End': True
    }

    step = EmrTerminateClusterStep('Terminate EMR cluster', wait_for_completion=False, parameters={
        'ClusterId': 'MyWorkflowClusterId'
    })

    assert step.to_dict() == {
        'Type': 'Task',
        'Resource': 'arn:aws:states:::elasticmapreduce:terminateCluster',
        'Parameters': {
            'ClusterId': 'MyWorkflowClusterId',
        },
        'End': True
    }


@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_emr_add_step_step_creation():
    step = EmrAddStepStep('Add step to EMR cluster', parameters={
        'ClusterId': 'MyWorkflowClusterId',
        'Step': {
            'Name': 'The first step',
            'ActionOnFailure': 'CONTINUE',
            'HadoopJarStep': {
                'Jar': 'command-runner.jar',
                'Args': [
                    'hive-script',
                    '--run-hive-script',
                    '--args',
                    '-f',
                    's3://<region>.elasticmapreduce.samples/cloudfront/code/Hive_CloudFront.q',
                    '-d',
                    'INPUT=s3://<region>.elasticmapreduce.samples',
                    '-d',
                    'OUTPUT=s3://<mybucket>/MyHiveQueryResults/'
                ]
            }
        }
    })

    assert step.to_dict() == {
        'Type': 'Task',
        'Resource': 'arn:aws:states:::elasticmapreduce:addStep.sync',
        'Parameters': {
            'ClusterId': 'MyWorkflowClusterId',
            'Step': {
                'Name': 'The first step',
                'ActionOnFailure': 'CONTINUE',
                'HadoopJarStep': {
                    'Jar': 'command-runner.jar',
                    'Args': [
                        'hive-script',
                        '--run-hive-script',
                        '--args',
                        '-f',
                        's3://<region>.elasticmapreduce.samples/cloudfront/code/Hive_CloudFront.q',
                        '-d',
                        'INPUT=s3://<region>.elasticmapreduce.samples',
                        '-d',
                        'OUTPUT=s3://<mybucket>/MyHiveQueryResults/'
                    ]
                }
            }
        },
        'End': True
    }

    step = EmrAddStepStep('Add step to EMR cluster', wait_for_completion=False, parameters={
        'ClusterId': 'MyWorkflowClusterId',
        'Step': {
            'Name': 'The first step',
            'ActionOnFailure': 'CONTINUE',
            'HadoopJarStep': {
                'Jar': 'command-runner.jar',
                'Args': [
                    'hive-script',
                    '--run-hive-script',
                    '--args',
                    '-f',
                    's3://<region>.elasticmapreduce.samples/cloudfront/code/Hive_CloudFront.q',
                    '-d',
                    'INPUT=s3://<region>.elasticmapreduce.samples',
                    '-d',
                    'OUTPUT=s3://<mybucket>/MyHiveQueryResults/'
                ]
            }
        }
    })

    assert step.to_dict() == {
        'Type': 'Task',
        'Resource': 'arn:aws:states:::elasticmapreduce:addStep',
        'Parameters': {
            'ClusterId': 'MyWorkflowClusterId',
            'Step': {
                'Name': 'The first step',
                'ActionOnFailure': 'CONTINUE',
                'HadoopJarStep': {
                    'Jar': 'command-runner.jar',
                    'Args': [
                        'hive-script',
                        '--run-hive-script',
                        '--args',
                        '-f',
                        's3://<region>.elasticmapreduce.samples/cloudfront/code/Hive_CloudFront.q',
                        '-d',
                        'INPUT=s3://<region>.elasticmapreduce.samples',
                        '-d',
                        'OUTPUT=s3://<mybucket>/MyHiveQueryResults/'
                    ]
                }
            }
        },
        'End': True
    }


@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_emr_cancel_step_step_creation():
    step = EmrCancelStepStep('Cancel step from EMR cluster', parameters={
        'ClusterId': 'MyWorkflowClusterId',
        'StepId': 'MyWorkflowStepId'
    })

    assert step.to_dict() == {
        'Type': 'Task',
        'Resource': 'arn:aws:states:::elasticmapreduce:cancelStep',
        'Parameters': {
            'ClusterId': 'MyWorkflowClusterId',
            'StepId': 'MyWorkflowStepId'
        },
        'End': True
    }


@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_emr_set_cluster_termination_protection_step_creation():
    step = EmrSetClusterTerminationProtectionStep('Set termination protection for EMR cluster', parameters={
        'ClusterId': 'MyWorkflowClusterId',
        'TerminationProtected': True
    })

    assert step.to_dict() == {
        'Type': 'Task',
        'Resource': 'arn:aws:states:::elasticmapreduce:setClusterTerminationProtection',
        'Parameters': {
            'ClusterId': 'MyWorkflowClusterId',
            'TerminationProtected': True
        },
        'End': True
    }


@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_emr_modify_instance_fleet_by_name_step_creation():
    step = EmrModifyInstanceFleetByNameStep('Modify Instance Fleet by name for EMR cluster', parameters={
        'ClusterId': 'MyWorkflowClusterId',
        'InstanceFleetName': 'MyCoreFleet',
        'InstanceFleet': {
            'TargetOnDemandCapacity': 8,
            'TargetSpotCapacity': 0
        }
    })

    assert step.to_dict() == {
        'Type': 'Task',
        'Resource': 'arn:aws:states:::elasticmapreduce:modifyInstanceFleetByName',
        'Parameters': {
            'ClusterId': 'MyWorkflowClusterId',
            'InstanceFleetName': 'MyCoreFleet',
            'InstanceFleet': {
                'TargetOnDemandCapacity': 8,
                'TargetSpotCapacity': 0
            }
        },
        'End': True
    }


@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_emr_modify_instance_group_by_name_step_creation():
    step = EmrModifyInstanceGroupByNameStep('Modify Instance Group by name for EMR cluster', parameters={
        'ClusterId': 'MyWorkflowClusterId',
        'InstanceGroupName': 'MyCoreGroup',
        'InstanceGroup': {
            'InstanceCount': 8
        }
    })

    assert step.to_dict() == {
        'Type': 'Task',
        'Resource': 'arn:aws:states:::elasticmapreduce:modifyInstanceGroupByName',
        'Parameters': {
            'ClusterId': 'MyWorkflowClusterId',
            'InstanceGroupName': 'MyCoreGroup',
            'InstanceGroup': {
                'InstanceCount': 8
            }
        },
        'End': True
    }


@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_databrew_start_job_run_step_creation_sync():
    step = GlueDataBrewStartJobRunStep('Start Glue DataBrew Job Run - Sync', parameters={
        "Name": "MyWorkflowJobRun"
    })

    assert step.to_dict() == {
        'Type': 'Task',
        'Resource': 'arn:aws:states:::databrew:startJobRun.sync',
        'Parameters': {
            'Name': 'MyWorkflowJobRun'
        },
        'End': True
    }


@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_databrew_start_job_run_step_creation():
    step = GlueDataBrewStartJobRunStep('Start Glue DataBrew Job Run', wait_for_completion=False, parameters={
        "Name": "MyWorkflowJobRun"
    })

    assert step.to_dict() == {
        'Type': 'Task',
        'Resource': 'arn:aws:states:::databrew:startJobRun',
        'Parameters': {
            'Name': 'MyWorkflowJobRun'
        },
        'End': True
    }


@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_eks_create_cluster_step_creation():
    step = EksCreateClusterStep("Create Eks cluster", wait_for_completion=False, parameters={
        'Name': 'MyCluster',
        'ResourcesVpcConfig': {
          'SubnetIds': [
            'subnet-00000000000000000',
            'subnet-00000000000000001'
          ]
        },
        'RoleArn': 'arn:aws:iam::123456789012:role/MyEKSClusterRole'
    })

    assert step.to_dict() == {
        'Type': 'Task',
        'Resource': 'arn:aws:states:::eks:createCluster',
        'Parameters': {
            'Name': 'MyCluster',
            'ResourcesVpcConfig': {
                'SubnetIds': [
                    'subnet-00000000000000000',
                    'subnet-00000000000000001'
                ]
            },
            'RoleArn': 'arn:aws:iam::123456789012:role/MyEKSClusterRole'
        },
        'End': True
    }


@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_eks_create_cluster_step_creation_sync():
    step = EksCreateClusterStep("Create Eks cluster sync", parameters={
        'Name': 'MyCluster',
        'ResourcesVpcConfig': {
          'SubnetIds': [
            'subnet-00000000000000000',
            'subnet-00000000000000001'
          ]
        },
        'RoleArn': 'arn:aws:iam::123456789012:role/MyEKSClusterRole'
    })

    assert step.to_dict() == {
        'Type': 'Task',
        'Resource': 'arn:aws:states:::eks:createCluster.sync',
        'Parameters': {
            'Name': 'MyCluster',
            'ResourcesVpcConfig': {
                'SubnetIds': [
                    'subnet-00000000000000000',
                    'subnet-00000000000000001'
                ]
            },
            'RoleArn': 'arn:aws:iam::123456789012:role/MyEKSClusterRole'
        },
        'End': True
    }


@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_eks_delete_cluster_step_creation():
    step = EksDeleteClusterStep("Delete Eks cluster", wait_for_completion=False, parameters={
        'Name': 'MyCluster'
    })

    assert step.to_dict() == {
        'Type': 'Task',
        'Resource': 'arn:aws:states:::eks:deleteCluster',
        'Parameters': {
            'Name': 'MyCluster'
        },
        'End': True
    }


@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_eks_delete_cluster_step_creation_sync():
    step = EksDeleteClusterStep("Delete Eks cluster sync", parameters={
        'Name': 'MyCluster'
    })

    assert step.to_dict() == {
        'Type': 'Task',
        'Resource': 'arn:aws:states:::eks:deleteCluster.sync',
        'Parameters': {
            'Name': 'MyCluster'
        },
        'End': True
    }


@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_eks_create_fargate_profile_step_creation():
    step = EksCreateFargateProfileStep("Create Fargate profile", wait_for_completion=False, parameters={
        'ClusterName': 'MyCluster',
        'FargateProfileName': 'MyFargateProfile',
        'PodExecutionRoleArn': 'arn:aws:iam::123456789012:role/MyFargatePodExecutionRole',
        'Selectors': [{
            'Namespace': 'my-namespace',
            'Labels': {'my-label': 'my-value'}
          }]
    })

    assert step.to_dict() == {
        'Type': 'Task',
        'Resource': 'arn:aws:states:::eks:createFargateProfile',
        'Parameters': {
            'ClusterName': 'MyCluster',
            'FargateProfileName': 'MyFargateProfile',
            'PodExecutionRoleArn': 'arn:aws:iam::123456789012:role/MyFargatePodExecutionRole',
            'Selectors': [{
                'Namespace': 'my-namespace',
                'Labels': {'my-label': 'my-value'}
            }]
        },
        'End': True
    }


@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_eks_create_fargate_profile_step_creation_sync():
    step = EksCreateFargateProfileStep("Create Fargate profile sync", parameters={
        'ClusterName': 'MyCluster',
        'FargateProfileName': 'MyFargateProfile',
        'PodExecutionRoleArn': 'arn:aws:iam::123456789012:role/MyFargatePodExecutionRole',
        'Selectors': [{
            'Namespace': 'my-namespace',
            'Labels': {'my-label': 'my-value'}
          }]
    })

    assert step.to_dict() == {
        'Type': 'Task',
        'Resource': 'arn:aws:states:::eks:createFargateProfile.sync',
        'Parameters': {
            'ClusterName': 'MyCluster',
            'FargateProfileName': 'MyFargateProfile',
            'PodExecutionRoleArn': 'arn:aws:iam::123456789012:role/MyFargatePodExecutionRole',
            'Selectors': [{
                'Namespace': 'my-namespace',
                'Labels': {'my-label': 'my-value'}
            }]
        },
        'End': True
    }


@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_eks_delete_fargate_profile_step_creation():
    step = EksDeleteFargateProfileStep("Delete Fargate profile", wait_for_completion=False, parameters={
        'ClusterName': 'MyCluster',
        'FargateProfileName': 'MyFargateProfile'
    })

    assert step.to_dict() == {
        'Type': 'Task',
        'Resource': 'arn:aws:states:::eks:deleteFargateProfile',
        'Parameters': {
            'ClusterName': 'MyCluster',
            'FargateProfileName': 'MyFargateProfile'
        },
        'End': True
    }


@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_eks_delete_fargate_profile_step_creation_sync():
    step = EksDeleteFargateProfileStep("Delete Fargate profile sync", parameters={
        'ClusterName': 'MyCluster',
        'FargateProfileName': 'MyFargateProfile'
    })

    assert step.to_dict() == {
        'Type': 'Task',
        'Resource': 'arn:aws:states:::eks:deleteFargateProfile.sync',
        'Parameters': {
            'ClusterName': 'MyCluster',
            'FargateProfileName': 'MyFargateProfile'
        },
        'End': True
    }


@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_eks_create_node_group_step_creation():
    step = EksCreateNodeGroupStep("Create Node Group", wait_for_completion=False, parameters={
        'ClusterName': 'MyCluster',
        'NodegroupName': 'MyNodegroup',
        'NodeRole': 'arn:aws:iam::123456789012:role/MyNodeInstanceRole',
        'Subnets': [
            'subnet-00000000000000000',
            'subnet-00000000000000001'
        ]
    })

    assert step.to_dict() == {
        'Type': 'Task',
        'Resource': 'arn:aws:states:::eks:createNodegroup',
        'Parameters': {
            'ClusterName': 'MyCluster',
            'NodegroupName': 'MyNodegroup',
            'NodeRole': 'arn:aws:iam::123456789012:role/MyNodeInstanceRole',
            'Subnets': [
                'subnet-00000000000000000',
                'subnet-00000000000000001'
            ],
        },
        'End': True
    }


def test_eks_create_node_group_step_creation_sync():
    step = EksCreateNodeGroupStep("Create Node Group sync", parameters={
        'ClusterName': 'MyCluster',
        'NodegroupName': 'MyNodegroup',
        'NodeRole': 'arn:aws:iam::123456789012:role/MyNodeInstanceRole',
        'Subnets': [
            'subnet-00000000000000000',
            'subnet-00000000000000001'
        ]
    })

    assert step.to_dict() == {
        'Type': 'Task',
        'Resource': 'arn:aws:states:::eks:createNodegroup.sync',
        'Parameters': {
            'ClusterName': 'MyCluster',
            'NodegroupName': 'MyNodegroup',
            'NodeRole': 'arn:aws:iam::123456789012:role/MyNodeInstanceRole',
            'Subnets': [
                'subnet-00000000000000000',
                'subnet-00000000000000001'
            ],
        },
        'End': True
    }

@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_eks_delete_node_group_step_creation():
    step = EksDeleteNodegroupStep("Delete Node Group", wait_for_completion=False, parameters={
        'ClusterName': 'MyCluster',
        'NodegroupName': 'MyNodegroup'
    })

    assert step.to_dict() == {
        'Type': 'Task',
        'Resource': 'arn:aws:states:::eks:deleteNodegroup',
        'Parameters': {
            'ClusterName': 'MyCluster',
            'NodegroupName': 'MyNodegroup'
        },
        'End': True
    }


@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_eks_delete_node_group_step_creation_sync():
    step = EksDeleteNodegroupStep("Delete Node Group sync", parameters={
        'ClusterName': 'MyCluster',
        'NodegroupName': 'MyNodegroup'
    })

    assert step.to_dict() == {
        'Type': 'Task',
        'Resource': 'arn:aws:states:::eks:deleteNodegroup.sync',
        'Parameters': {
            'ClusterName': 'MyCluster',
            'NodegroupName': 'MyNodegroup'
        },
        'End': True
    }


@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_eks_run_job_step_creation():
    step = EksRunJobStep("Run Job", wait_for_completion=False, parameters={
        'ClusterName': 'MyCluster',
        'CertificateAuthority': 'ANPAJ2UCCR6DPCEXAMPLE',
        'Endpoint': 'https://AKIAIOSFODNN7EXAMPLE.yl4.us-east-1.eks.amazonaws.com',
        'Job': {
            'apiVersion': 'batch/v1',
            'kind': 'Job',
            'metadata': {
                'name': 'example-job'
            },
            'spec': {
                'backoffLimit': 0,
                'template': {
                    'metadata': {
                        'name': 'example-job'
                    },
                    'spec': {
                        'containers': [
                            {
                                'name': 'pi-2000',
                                'image': 'perl',
                                'command': ['perl'],
                                'args': [
                                    '-Mbignum=bpi',
                                    '-wle',
                                    'print bpi(2000)'
                                ]
                            }
                        ],
                        'restartPolicy': 'Never'
                    }
                }
            }
        }
    })

    assert step.to_dict() == {
        'Type': 'Task',
        'Resource': 'arn:aws:states:::eks:runJob',
        'Parameters': {
            'CertificateAuthority': 'ANPAJ2UCCR6DPCEXAMPLE',
            'ClusterName': 'MyCluster',
            'Endpoint': 'https://AKIAIOSFODNN7EXAMPLE.yl4.us-east-1.eks.amazonaws.com',
            'Job': {
                'apiVersion': 'batch/v1',
                'kind': 'Job',
                'metadata': {'name': 'example-job'},
                'spec': {
                    'backoffLimit': 0,
                    'template': {
                        'metadata': {'name': 'example-job'},
                        'spec': {
                            'containers': [{
                                'args': ['-Mbignum=bpi',
                                         '-wle',
                                         'print '
                                         'bpi(2000)'],
                                'command': ['perl'],
                                'image': 'perl',
                                'name': 'pi-2000'}],
                            'restartPolicy': 'Never'}
                    }
                }
            }
        },
        'End': True
    }


@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_eks_run_job_step_creation_sync():
    step = EksRunJobStep("Run Job sync", parameters={
        'ClusterName': 'MyCluster',
        'CertificateAuthority': 'ANPAJ2UCCR6DPCEXAMPLE',
        'Endpoint': 'https://AKIAIOSFODNN7EXAMPLE.yl4.us-east-1.eks.amazonaws.com',
        'LogOptions': {
            'RetrieveLogs': True
        },
        'Job': {
            'apiVersion': 'batch/v1',
            'kind': 'Job',
            'metadata': {
                'name': 'example-job'
            },
            'spec': {
                'backoffLimit': 0,
                'template': {
                    'metadata': {
                        'name': 'example-job'
                    },
                    'spec': {
                        'containers': [
                            {
                                'name': 'pi-2000',
                                'image': 'perl',
                                'command': ['perl'],
                                'args': [
                                    '-Mbignum=bpi',
                                    '-wle',
                                    'print bpi(2000)'
                                ]
                            }
                        ],
                        'restartPolicy': 'Never'
                    }
                }
            }
        }
    })

    assert step.to_dict() == {
        'Type': 'Task',
        'Resource': 'arn:aws:states:::eks:runJob.sync',
        'Parameters': {
            'CertificateAuthority': 'ANPAJ2UCCR6DPCEXAMPLE',
            'ClusterName': 'MyCluster',
            'Endpoint': 'https://AKIAIOSFODNN7EXAMPLE.yl4.us-east-1.eks.amazonaws.com',
            'LogOptions': {
                'RetrieveLogs': True
            },
            'Job': {
                'apiVersion': 'batch/v1',
                'kind': 'Job',
                'metadata': {'name': 'example-job'},
                'spec': {
                    'backoffLimit': 0,
                    'template': {
                        'metadata': {'name': 'example-job'},
                        'spec': {
                            'containers': [{
                                'args': ['-Mbignum=bpi',
                                         '-wle',
                                         'print '
                                         'bpi(2000)'],
                                'command': ['perl'],
                                'image': 'perl',
                                'name': 'pi-2000'}],
                            'restartPolicy': 'Never'}
                    }
                }
            }
        },
        'End': True
    }


@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_eks_call_step_creation():
    step = EksCallStep("Call", parameters={
        'ClusterName': 'MyCluster',
        'CertificateAuthority': 'ANPAJ2UCCR6DPCEXAMPLE',
        'Endpoint': 'https://444455556666.yl4.us-east-1.eks.amazonaws.com',
        'Method': 'GET',
        'Path': '/api/v1/namespaces/default/pods',
        'QueryParameters': {
            'labelSelector': [
                'job-name=example-job'
            ]
        }
    })

    assert step.to_dict() == {
        'Type': 'Task',
        'Resource': 'arn:aws:states:::eks:call',
        'Parameters': {
            'ClusterName': 'MyCluster',
            'CertificateAuthority': 'ANPAJ2UCCR6DPCEXAMPLE',
            'Endpoint': 'https://444455556666.yl4.us-east-1.eks.amazonaws.com',
            'Method': 'GET',
            'Path': '/api/v1/namespaces/default/pods',
            'QueryParameters': {
                'labelSelector': [
                    'job-name=example-job'
                ]
            }
        },
        'End': True
    }


@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_step_functions_start_execution_step_creation_default():
    step = StepFunctionsStartExecutionStep(
        "SFN Start Execution", parameters={
            "StateMachineArn": "arn:aws:states:us-east-1:123456789012:stateMachine:HelloWorld",
            "Name": "ExecutionName"
        })

    assert step.to_dict() == {
        "Type": "Task",
        "Resource": "arn:aws:states:::states:startExecution.sync:2",
        "Parameters": {
            "StateMachineArn": "arn:aws:states:us-east-1:123456789012:stateMachine:HelloWorld",
            "Name": "ExecutionName"
        },
        "End": True
    }


@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_step_functions_start_execution_step_creation_call_and_continue():
    step = StepFunctionsStartExecutionStep(
        "SFN Start Execution", integration_pattern=IntegrationPattern.CallAndContinue, parameters={
            "StateMachineArn": "arn:aws:states:us-east-1:123456789012:stateMachine:HelloWorld",
            "Name": "ExecutionName"
        })

    assert step.to_dict() == {
        "Type": "Task",
        "Resource": "arn:aws:states:::states:startExecution",
        "Parameters": {
            "StateMachineArn": "arn:aws:states:us-east-1:123456789012:stateMachine:HelloWorld",
            "Name": "ExecutionName"
        },
        "End": True
    }


@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_step_functions_start_execution_step_creation_wait_for_completion():
    step = StepFunctionsStartExecutionStep(
        "SFN Start Execution - Sync", integration_pattern=IntegrationPattern.WaitForCompletion, parameters={
            "StateMachineArn": "arn:aws:states:us-east-1:123456789012:stateMachine:HelloWorld",
            "Name": "ExecutionName"
        })

    assert step.to_dict() == {
        "Type": "Task",
        "Resource": "arn:aws:states:::states:startExecution.sync:2",
        "Parameters": {
            "StateMachineArn": "arn:aws:states:us-east-1:123456789012:stateMachine:HelloWorld",
            "Name": "ExecutionName"
        },
        "End": True
    }


@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_step_functions_start_execution_step_creation_wait_for_task_token():
    step = StepFunctionsStartExecutionStep(
        "SFN Start Execution - Wait for Callback", integration_pattern=IntegrationPattern.WaitForTaskToken,
        parameters={
            "Input": {
                "token.$": "$$.Task.Token"
            },
            "StateMachineArn": "arn:aws:states:us-east-1:123456789012:stateMachine:HelloWorld",
            "Name": "ExecutionName"
        })

    assert step.to_dict() == {
        "Type": "Task",
        "Resource": "arn:aws:states:::states:startExecution.waitForTaskToken",
        "Parameters": {
            "Input": {
                "token.$": "$$.Task.Token"
            },
            "StateMachineArn": "arn:aws:states:us-east-1:123456789012:stateMachine:HelloWorld",
            "Name": "ExecutionName"
        },
        "End": True
    }


@pytest.mark.parametrize("integration_pattern", [
    None,
    "ServiceIntegrationTypeStr",
    0
])
@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_step_functions_start_execution_step_creation_invalid_integration_pattern_raises_type_error(integration_pattern):
    with pytest.raises(TypeError):
        StepFunctionsStartExecutionStep("SFN Start Execution - invalid ServiceType", integration_pattern=integration_pattern)
