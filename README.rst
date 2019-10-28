|codebuild|

=============================
AWS Data Science Workflow SDK
=============================

The AWS Data Science Workflows SDK is an open source library that allows data
scientists to easily create workflows that process and publish machine learning
models using AWS SageMaker and AWS StepFunctions. You can create create
multi-step machine learning workflows in Python that orchestrate AWS
infrastructure at scale, without having to provision and integrate the AWS
services separately.

The AWS Data Science Workflows Python SDK allows you to do the following.

- Easily construct and run machine learning workflows that use AWS infrastructure directly in  Python
- Instantiate common training pipelines
- Create standard machine learning workflows in a Jupyter notebook from templates
- Export workflow templates that create AWS resources using AWS CloudFormation

1. `AWS Step Functions`_
2. `Installing the AWS Data Science Workflows SDK`_
3. `Using the AWS Data Science Workflows SDK`_
4. `Supported Operating Systems`_
5. `Supported Python Versions`_
6. `AWS Permissions`_
7. `Licensing`_ 

AWS Step Functions
------------------
AWS Step Functions lets you coordinate multiple AWS services into serverless
workflows so you can build and update apps quickly. Using Step Functions, you
can design and run workflows that stitch together services such as Amazon
SageMaker, AWS Lambda and Amazon ECS into feature-rich applications. Workflows
are made up of a series of steps, with the output of one step acting as input
into the next.

The AWS Data Science Workflow SDK provides access to Step Functions,
so that you can easily create and run machine learning, and data science workflows 
directly in Python, and inside your Jupyter Notebooks.

For more information, see the Step Functions `documentation`_.

.. _documentation: https://docs.aws.amazon.com/step-functions/index.html


Installing the AWS Data Science Workflows SDK
---------------------------------------------

The AWS Data Science Workflow SDK is built to PyPI and can be installed with pip as follows.

::

	pip install stepfunctions

You can install from source by cloning this repository and running a pip install command in the root directory of the repository:

::

    git clone https://github.com/aws/stepfunctions-sdk.git
    cd stepfunctions-sdk
    pip install .


Using the AWS Data Science Workflows SDK
----------------------------------------


Supported Operating Systems
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The AWS Data Science Workflow SDK supports Unix/Linux and Mac.

Supported Python Versions
~~~~~~~~~~~~~~~~~~~~~~~~~

The AWS Data Science Workflow SDK is tested on:

- Python 3.6

AWS Permissions
~~~~~~~~~~~~~~~

As a managed service, AWS Step Functions performs operations on your behalf on the AWS hardware that is managed by AWS Step Functions.
AWS Step Functions can perform only operations that the user permits.
You can read more about which permissions are necessary in the `AWS Documentation <https://docs.aws.amazon.com/step-functions/latest/dg/security.html>`__.

The AWS Data Science Workflows SDK should not require any additional permissions aside from what is required for using .AWS Step Functions.
However, if you are using an IAM role with a path in it, you should grant permission for ``iam:GetRole``.

Licensing
~~~~~~~~~
AWS Data Science Workflows SDK is licensed under the Apache 2.0 License. It is copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved. The license is available at:
http://aws.amazon.com/apache2.0/


.. |codebuild| image:: https://codebuild.us-east-2.amazonaws.com/badges?uuid=eyJlbmNyeXB0ZWREYXRhIjoiUkFzRXd6UmdKZkJIZFRPMTRCMmhKYzJqL1U0bEpMdDFvSGJPeXBCSlhQaDBaQVZxYWtnUkZNMmhlclRSeGxCbjZhVTl0dlpiQXFKd1puUFZJK0xmNHN3PSIsIml2UGFyYW1ldGVyU3BlYyI6ImZ2ekJpa3V5ZXgxV3gyczUiLCJtYXRlcmlhbFNldFNlcmlhbCI6MX0%3D&branch=master
