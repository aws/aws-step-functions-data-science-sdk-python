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

from stepfunctions.steps.service import DynamoDBGetItemStep, DynamoDBPutItemStep, DynamoDBUpdateItemStep, DynamoDBDeleteItemStep
from stepfunctions.steps.service import SnsPublishStep, SqsSendMessageStep


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
