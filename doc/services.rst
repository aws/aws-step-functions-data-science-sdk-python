Service Integrations
=====================

This module provides classes to build steps that integrate with Amazon DynamoDB, Amazon SNS, Amazon SQS and Amazon EMR.


**Table of Contents**

- `Amazon DynamoDB <#amazon-dynamodb>`__

- `Amazon SNS <#amazon-sns>`__

- `Amazon SQS <#amazon-sqs>`__

- `Amazon EMR <#amazon-emr>`__


Amazon DynamoDB
----------------
.. autoclass:: stepfunctions.steps.service.DynamoDBGetItemStep

.. autoclass:: stepfunctions.steps.service.DynamoDBPutItemStep

.. autoclass:: stepfunctions.steps.service.DynamoDBDeleteItemStep

.. autoclass:: stepfunctions.steps.service.DynamoDBUpdateItemStep

Amazon SNS
-----------
.. autoclass:: stepfunctions.steps.service.SnsPublishStep

Amazon SQS
-----------
.. autoclass:: stepfunctions.steps.service.SqsSendMessageStep

Amazon EMR
-----------
.. autoclass:: stepfunctions.steps.service.EmrCreateClusterStep

.. autoclass:: stepfunctions.steps.service.EmrTerminateClusterStep

.. autoclass:: stepfunctions.steps.service.EmrAddStepStep

.. autoclass:: stepfunctions.steps.service.EmrCancelStepStep

.. autoclass:: stepfunctions.steps.service.EmrSetClusterTerminationProtectionStep

.. autoclass:: stepfunctions.steps.service.EmrModifyInstanceFleetByNameStep

.. autoclass:: stepfunctions.steps.service.EmrModifyInstanceGroupByNameStep
