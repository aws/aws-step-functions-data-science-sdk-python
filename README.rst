|codebuild|

===================================
AWS Step Functions Data Science SDK
===================================

The AWS Step Functions Data Science SDK is an open-source library that allows data
scientists to easily create workflows that process and publish machine learning
models using Amazon SageMaker and AWS Step Functions. You can create machine learning
workflows in Python that orchestrate AWS infrastructure at scale, without having
to provision and integrate the AWS services separately.

* Workflow - A sequence of steps designed to perform some work
* Step - A unit of work within a workflow
* ML Pipeline - A type of workflow used in data science to create and train machine learning models

The AWS Step Functions Data Science SDK enables you to do the following.

- Easily construct and run machine learning workflows that use AWS
  infrastructure directly in  Python
- Instantiate common training pipelines
- Create standard machine learning workflows in a Jupyter notebook from
  templates

Table of Contents
-----------------
- `Getting Started With Sample Jupyter Notebooks <#getting-started-with-sample-jupyter-notebooks>`__
- `Installing the AWS Step Functions Data Science SDK <#installing-the-aws-data-science-workflows-sdk>`__
- `Overview <#overview>`__
- `AWS Permissions <#aws-permissions>`__
- `Licensing <#licensing>`__
- `Verifying the Signature <#verifying-the-signature>`__

Getting Started With Sample Jupyter Notebooks
---------------------------------------------

The best way to quickly review how the AWS Step Functions Data Science SDK works
is to review the related example notebooks. These notebooks provide code and
descriptions for creating and running workflows in AWS Step Functions Using
the AWS Step Functions Data Science SDK.

Example Notebooks in SageMaker
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In Amazon SageMaker, example Jupyter notebooks are available in the **example
notebooks** portion of a notebook instance. To run the example notebooks, do the following.

1. Either `Create a Notebook Instance <https://docs.aws.amazon.com/sagemaker/latest/dg/gs-setup-working-env.html>`__ or `Access an Existing <https://docs.aws.amazon.com/sagemaker/latest/dg/howitworks-access-ws.html>`__ notebook instance.

2. Select the **SageMaker Examples** tab.

3. Choose a notebook in the **Step Functions Data Science SDK** section and select **Use**.

For more information, see `Example Notebooks <https://docs.aws.amazon.com/sagemaker/latest/dg/howitworks-nbexamples.html>`__
in the Amazon SageMaker documentation.


Run Example Notebooks Locally
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To run the AWS Step Functions Data Science SDK example notebooks locally, download
the sample notebooks and open them in a working Jupyter instance.

1. Install Jupyter: https://jupyter.readthedocs.io/en/latest/install.html

2. Download the following files from:
   https://github.com/awslabs/amazon-sagemaker-examples/tree/master/step-functions-data-science-sdk.

  * :code:`hello_world_workflow.ipynb`
  * :code:`machine_learning_workflow_abalone.ipynb`
  * :code:`training_pipeline_pytorch_mnist.ipynb`

3. Open the files in Jupyter.



Installing the AWS Step Functions Data Science SDK
--------------------------------------------------

The AWS Step Functions Data Science SDK is built to PyPI and can be installed with
pip as follows.


::

        pip install stepfunctions

You can install from source by cloning this repository and running a pip install
command in the root directory of the repository:

::

    git clone https://github.com/aws/aws-step-functions-data-science-sdk-python.git
    cd aws-step-functions-data-science-sdk-python
    pip install .

Supported Operating Systems
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The AWS Step Functions Data Science SDK supports Unix/Linux and Mac.

Supported Python Versions
~~~~~~~~~~~~~~~~~~~~~~~~~

The AWS Step Functions Data Science SDK is tested on:

* Python 2.7
* Python 3.6

Overview of SDK
---------------

The AWS Step Functions Data Science SDK provides a Python API that enables you to
create data science and machine learning workflows using AWS Step Functions and
SageMaker directly in your Python code and Jupyter notebooks.

Using this SDK you can:

1. Create steps that accomplish tasks.
2. Chain those steps together into workflows.
3. Include retry, succeed, or fail steps.
4. Review a graphical representation and definition for your workflow.
5. Create a workflow in AWS Step Functions.
6. Start and review executions in AWS Step Functions.

For a detailed API reference of the AWS Step Functions Data Science SDK,
be sure to view this documentation on
`Read the Docs <https://aws-step-functions-data-science.readthedocs.io>`_.


AWS Step Functions
~~~~~~~~~~~~~~~~~~

AWS Step Functions lets you coordinate multiple AWS services into serverless
workflows so you can build and update apps quickly. Using Step Functions, you
can design and run workflows that combine services such as Amazon SageMaker, AWS
Lambda, and Amazon Elastic Container Service (Amazon ECS), into feature-rich
applications. Workflows are made up of a series of steps, with the output of one
step acting as input to the next.

The AWS Step Functions Data Science SDK provides access to AWS Step Functions so that
you can easily create and run machine learning and data science workflows
directly in Python, and inside your Jupyter Notebooks. Workflows are created locally
in Python, but when they are ready for execution, the workflow is first uploaded
to the AWS Step Functions service for execution in the cloud.

When you use the SDK to create, update, or execute workflows
you are talking to the Step Functions service in the cloud. Your workflows
live in AWS Step Functions and can be re-used.

You can execute a workflow as many times as you want, and you can optionally
change the input each time. Each time you execute a workflow, it creates a new
execution instance in the cloud. You can inspect these executions with SDK
commands, or with the Step Functions management console. You can run more than
one execution at a time.

Using this SDK you can create steps, chain them together to create a workflow,
create that workflow in AWS Step Functions, and execute the workflow in the
AWS cloud.

.. image:: images/create.png
  :width: 400
  :alt: Create a workflow in AWS Step Functions

Once you have created your workflow in AWS Step Functions, you can execute that
workflow in Step Functions, in the AWS cloud.

.. image:: images/execute.png
  :width: 400
  :alt: Start a workflow in AWS Step Functions

Step Functions creates workflows out of steps called `States <https://docs.aws.amazon.com/step-functions/latest/dg/concepts-states.html>`__,
and expresses that workflow in the `Amazon States Language <https://docs.aws.amazon.com/step-functions/latest/dg/concepts-amazon-states-language.html>`__.
When you create a workflow in the AWS Step Functions Data Science SDK, it
creates a State Machine representing your workflow and steps in AWS Step
Functions.

For more information about Step Functions concepts and use, see the Step
Functions `documentation`_.

.. _documentation: https://docs.aws.amazon.com/step-functions/index.html

Building a Workflow
-------------------

Steps
~~~~~

You create steps using the SDK, and chain them together into sequential
workflows. Then, you can create those workflows in AWS Step Functions and
execute them in Step Functions directly from your Python code. For example,
the following is how you define a pass step.

.. code-block:: python

    start_pass_state = Pass(
        state_id="MyPassState"
    )

The following is how you define a wait step.


.. code-block:: python

    wait_state = Wait(
        state_id="Wait for 3 seconds",
        seconds=3
    )

The following example shows how to define a Lambda step,
and then defines a `Retry` and a `Catch`.

.. code-block:: python

    lambda_state = LambdaStep(
        state_id="Convert HelloWorld to Base64",
        parameters={
            "FunctionName": "MyLambda", #replace with the name of your function
            "Payload": {
            "input": "HelloWorld"
            }
        }
    )

    lambda_state.add_retry(Retry(
        error_equals=["States.TaskFailed"],
        interval_seconds=15,
        max_attempts=2,
        backoff_rate=4.0
    ))

    lambda_state.add_catch(Catch(
        error_equals=["States.TaskFailed"],
        next_step=Fail("LambdaTaskFailed")
    ))

Workflows
~~~~~~~~~

After you define these steps, chain them together into a logical sequence.

.. code-block:: python

    workflow_definition=Chain([start_pass_state, wait_state, lambda_state])

Once the steps are chained together, you can define the workflow definition.

.. code-block:: python

     workflow = Workflow(
         name="MyWorkflow_v1234",
         definition=workflow_definition,
         role=stepfunctions_execution_role
     )

Visualizing a Workflow
~~~~~~~~~~~~~~~~~~~~~~

The following generates a graphical representation of your workflow.

.. code-block:: python

  workflow.render_graph(portrait=False)

Review a Workflow Definition
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following renders the JSON of the `Amazon States Language
<https://docs.aws.amazon.com/step-functions/latest/dg/concepts-amazon-states-language.html>`__
definition of the workflow you created.

.. code-block:: python

  print(workflow.definition.to_json(pretty=True))

Running a Workflow
-------------------

Create Workflow on AWS Step Functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following creates the workflow in AWS Step Functions.

.. code-block:: python

  workflow.create()

Execute the Workflow
~~~~~~~~~~~~~~~~~~~~

The following starts an execution of your workflow in AWS Step Functions.

.. code-block:: python

  execution = workflow.execute(inputs={
    "IsHelloWorldExample": True
  })

Export an AWS CloudFormation Template
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following generates an AWS CloudFormation Template to deploy your workflow.

.. code-block:: python

  get_cloudformation_template()

The  generated template contains only the StateMachine resource. To reuse
the CloudFormation template in a different region, please make sure to update
the region specific AWS resources (such as the Lambda ARN and Training Image)
in the StateMachine definition.

AWS Permissions
---------------
As a managed service, AWS Step Functions performs operations on your behalf on
AWS hardware that is managed by AWS Step Functions.  AWS Step Functions can
perform only operations that the user permits.  You can read more about which
permissions are necessary in the `AWS Documentation
<https://docs.aws.amazon.com/step-functions/latest/dg/security.html>`__.

The AWS Step Functions Data Science SDK should not require any additional permissions
aside from what is required for using .AWS Step Functions.  However, if you are
using an IAM role with a path in it, you should grant permission for
``iam:GetRole``.

Licensing
---------
AWS Step Functions Data Science SDK is licensed under the Apache 2.0 License. It is
copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved. The
license is available at: http://aws.amazon.com/apache2.0/

Verifying the Signature
-----------------------

.. include:: signing.rst

.. |codebuild| image:: https://codebuild.us-east-2.amazonaws.com/badges?uuid=eyJlbmNyeXB0ZWREYXRhIjoiUkFzRXd6UmdKZkJIZFRPMTRCMmhKYzJqL1U0bEpMdDFvSGJPeXBCSlhQaDBaQVZxYWtnUkZNMmhlclRSeGxCbjZhVTl0dlpiQXFKd1puUFZJK0xmNHN3PSIsIml2UGFyYW1ldGVyU3BlYyI6ImZ2ekJpa3V5ZXgxV3gyczUiLCJtYXRlcmlhbFNldFNlcmlhbCI6MX0%3D&branch=master
