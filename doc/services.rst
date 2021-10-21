Service Integrations
=====================

This module provides classes to build steps that integrate with Amazon DynamoDB, Amazon SNS, Amazon SQS and Amazon EMR.


**Table of Contents**

- `Amazon DynamoDB <#amazon-dynamodb>`__

- `Amazon EKS <#amazon-eks>`__

- `Amazon EMR <#amazon-emr>`__

- `Amazon EventBridge <#amazon-eventbridge>`__

- `AWS Glue DataBrew <#aws-glue-databrew>`__

- `Amazon SNS <#amazon-sns>`__

- `Amazon SQS <#amazon-sqs>`__

- `AWS Step Functions <#aws-step-functions>`__


Amazon DynamoDB
----------------
.. autoclass:: stepfunctions.steps.service.DynamoDBGetItemStep

.. autoclass:: stepfunctions.steps.service.DynamoDBPutItemStep

.. autoclass:: stepfunctions.steps.service.DynamoDBDeleteItemStep

.. autoclass:: stepfunctions.steps.service.DynamoDBUpdateItemStep


Amazon EKS
----------
.. autoclass:: stepfunctions.steps.service.EksCallStep

.. autoclass:: stepfunctions.steps.service.EksCreateClusterStep

.. autoclass:: stepfunctions.steps.service.EksCreateFargateProfileStep

.. autoclass:: stepfunctions.steps.service.EksCreateNodeGroupStep

.. autoclass:: stepfunctions.steps.service.EksDeleteClusterStep

.. autoclass:: stepfunctions.steps.service.EksDeleteFargateProfileStep

.. autoclass:: stepfunctions.steps.service.EksDeleteNodegroupStep

.. autoclass:: stepfunctions.steps.service.EksRunJobStep


Amazon EMR
-----------
.. autoclass:: stepfunctions.steps.service.EmrCreateClusterStep

.. autoclass:: stepfunctions.steps.service.EmrTerminateClusterStep

.. autoclass:: stepfunctions.steps.service.EmrAddStepStep

.. autoclass:: stepfunctions.steps.service.EmrCancelStepStep

.. autoclass:: stepfunctions.steps.service.EmrSetClusterTerminationProtectionStep

.. autoclass:: stepfunctions.steps.service.EmrModifyInstanceFleetByNameStep

.. autoclass:: stepfunctions.steps.service.EmrModifyInstanceGroupByNameStep

Amazon EventBridge
-----------
.. autoclass:: stepfunctions.steps.service.EventBridgePutEventsStep

AWS Glue DataBrew
--------------------
.. autoclass:: stepfunctions.steps.service.GlueDataBrewStartJobRunStep

Amazon SNS
-----------
.. autoclass:: stepfunctions.steps.service.SnsPublishStep

Amazon SQS
-----------
.. autoclass:: stepfunctions.steps.service.SqsSendMessageStep

AWS Step Functions
------------------
.. autoclass:: stepfunctions.steps.service.StepFunctionsStartExecutionStep

