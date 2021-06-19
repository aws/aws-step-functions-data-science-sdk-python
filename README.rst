|codebuild|  |readthedocs|  |pypi|

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
  infrastructure directly in Python
- Instantiate common training pipelines
- Create standard machine learning workflows in a Jupyter notebook from
  templates

Table of Contents
-----------------
- `Getting Started With Sample Jupyter Notebooks <#getting-started-with-sample-jupyter-notebooks>`__
- `Installing the AWS Step Functions Data Science SDK <#installing-the-aws-step-functions-data-science-sdk>`__
- `Overview of SDK <#overview-of-sdk>`__
- `Contributing <#contributing>`__
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
`Read the Docs <https://aws-step-functions-data-science-sdk.readthedocs.io>`_.


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

.. image:: doc/images/create.png
    :width: 600
    :alt: Create a workflow in AWS Step Functions

Once you have created your workflow in AWS Step Functions, you can execute that
workflow in Step Functions, in the AWS cloud.

.. image:: doc/images/execute.png
    :width: 600
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

The following generates a graphical representation of your workflow. Please note that visualization currently only works in Jupyter notebooks. Visualization is not available in JupyterLab.

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

Contributing
------------
We welcome community contributions and pull requests. See
`CONTRIBUTING.md <https://github.com/aws/aws-step-functions-data-science-sdk-python/blob/main/CONTRIBUTING.md>`__ for
information on how to set up a development environment, run tests and submit code.

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

This section describes the recommended process of verifying the validity of the
AWS Data Science Workflows Python SDK's compiled distributions on
`PyPI <https://pypi.org/project/stepfunctions/>`__.

Whenever you download an application from the internet, we recommend that you
authenticate the identity of the software publisher and check that the
application is not altered or corrupted since it was published. This protects
you from installing a version of the application that contains a virus or other
malicious code.

If after running the steps in this topic, you determine that the distribution
for the AWS Data Science Workflows Python SDK is altered or corrupted, do NOT
install the package. Instead, contact AWS Support (https://aws.amazon.com/contact-us/).

AWS Data Science Workflows Python SDK distributions on PyPI are signed using
GnuPG, an open source implementation of the Pretty Good Privacy (OpenPGP)
standard for secure digital signatures. GnuPG (also known as GPG) provides
authentication and integrity checking through a digital signature. For more
information about PGP and GnuPG (GPG), see http://www.gnupg.org.

The first step is to establish trust with the software publisher. Download the
public key of the software publisher, check that the owner of the public key is
who they claim to be, and then add the public key to your keyring. Your keyring
is a collection of known public keys. After you establish the authenticity of
the public key, you can use it to verify the signature of the application.

Topics
~~~~~~

1. `Installing the GPG Tools <#installing-the-gpg-tools>`__
2. `Authenticating and Importing the Public Key <#authenticating-and-importing-the-public-key>`__
3. `Verify the Signature of the Package <#verify-the-signature-of-the-package>`__

Installing the GPG Tools
~~~~~~~~~~~~~~~~~~~~~~~~

If your operating system is Linux or Unix, the GPG tools are likely already
installed. To test whether the tools are installed on your system, type
**gpg** at a command prompt. If the GPG tools are installed, you see a GPG
command prompt. If the GPG tools are not installed, you see an error stating
that the command cannot be found. You can install the GnuPG package from a
repository.

**To install GPG tools on Debian-based Linux**

From a terminal, run the following command: **apt-get install gnupg**

**To install GPG tools on Red Hat–based Linux**

From a terminal, run the following command: **yum install gnupg**

Authenticating and Importing the Public Key
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The next step in the process is to authenticate the AWS Data Science Workflows
Python SDK public key and add it as a trusted key in your GPG keyring.

To authenticate and import the AWS Data Science Workflows Python SDK public key

1. Copy the key from the following text and paste it into a file called
`data_science_workflows.key`. Make sure to include everything that follows:

.. code-block:: text

  -----BEGIN PGP PUBLIC KEY BLOCK-----

  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
  /vQojRxttMc=
  =ovUh
  -----END PGP PUBLIC KEY BLOCK-----


2. At a command prompt in the directory where you saved
`data_science_workflows.key`, use the following command to import the AWS Data
Science Workflows Python SDK public key into your keyring:

.. code-block:: text

  gpg --import data_science_workflows.key

The command returns results that are similar to the following:

.. code-block:: text

  gpg: key 60EB103AE314A809: public key "Stepfunctions-Python-SDK-Signing <stepfunctions-developer-experience [at] amazon.com>" imported
  gpg: Total number processed: 1
  gpg:               imported: 1

Make a note of the key value; you need it in the next step. In the preceding
example, the key value is 60EB103AE314A809.

3. Verify the fingerprint by running the following command, replacing key-value
with the value from the preceding step:

.. code-block:: text

  gpg --fingerprint <key-value>

This command returns results similar to the following:

.. code-block:: text

  pub   rsa4096 2019-10-31 [SC] [expires: 2030-10-31] CC16 0577 B7BF 9D3D 6E5D
  51C5 60EB 103A E314 A809 uid           [ unknown]
  Stepfunctions-Python-SDK-Signing
  <stepfunctions-developer-experience [at] amazon.com> sub   rsa4096 2019-10-31 [E]
  [expires: 2030-10-31]

Additionally, the fingerprint string should be identical to CC16 0577 B7BF
9D3D 6E5D  51C5 60EB 103A E314 A809, as shown in the preceding example.
Compare the key fingerprint that is returned to the one published on this
page. They should match. If they don't match, don't install the AWS Data
Science Workflows Python SDK package, and contact AWS Support.

Verify the Signature of the Package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

After you install the GPG tools, authenticate and import the AWS Data Science
Workflows Python SDK public key, and verify that the public key is trusted, you
are ready to verify the signature of the package.

To verify the package signature, do the following.

1. Download the detached signature for the package from PyPI

  Go to the downloads section for the Data Science Workflows Python SDK
  https://pypi.org/project/stepfunctions/#files on PyPI, Right-click on the SDK
  distribution link, and choose "Copy Link Location/Address".

  Append the string ".asc" to the end of the link you copied, and paste this
  new link on your browser.

  Your browser will prompt you to download a file, which is the detatched
  signature associated with the respective distribution. Save the file on your
  local machine.

2. Verify the signature by running the following command at a command prompt
in the directory where you saved signature file and the AWS Data Science
Workflows Python SDK installation file. Both files must be present.

.. code-block:: text

  gpg --verify <path-to-detached-signature-file>

The output should look something like the following:

.. code-block:: text

  gpg: Signature made Thu 31 Oct 12:14:53 2019 PDT
  gpg:                using RSA key CC160577B7BF9D3D6E5D51C560EB103AE314A809
  gpg: Good signature from "Stepfunctions-Python-SDK-Signing <stepfunctions-developer-experience [at] amazon.com>" [unknown]
  gpg: WARNING: This key is not certified with a trusted signature!
  gpg:          There is no indication that the signature belongs to the owner.
  Primary key fingerprint: CC16 0577 B7BF 9D3D 6E5D  51C5 60EB 103A E314 A809

If the output contains the phrase Good signature from "AWS Data Science
Workflows Python SDK <stepfunctions-developer-experience [at] amazon.com>", it means
that the signature has successfully been verified, and you can proceed to run
the AWS Data Science Workflows Python SDK package.

If the output includes the phrase BAD signature, check whether you performed the
procedure correctly. If you continue to get this response, don't run the
installation file that you downloaded previously, and contact AWS Support.

The following are details about the warnings you might see:

.. code-block:: text

  WARNING: This key is not certified with a trusted signature! There is no
  indication that the signature belongs to the owner. This refers to your
  personal level of trust in your belief that you possess an authentic public
  key for AWS Data Science Workflows Python SDK. In an ideal world, you would
  visit an AWS office and receive the key in person. However, more often you
  download it from a website. In this case, the website is an AWS website.

  gpg: no ultimately trusted keys found. This means that the specific key is not
  "ultimately trusted" by you (or by other people whom you trust).

For more information, see http://www.gnupg.org.

.. |codebuild| image:: https://codebuild.us-east-2.amazonaws.com/badges?uuid=eyJlbmNyeXB0ZWREYXRhIjoiZ2crZkxWN2lPTHhBdzAwOUIvZDlUQ2txQTRyYnZnQ3RaQ0dQYkhsb2EvT04xOVRIdDBqYWFOaS8weklGU216OUtuc29pZFQvQjgrRDhRbWJoeEJocFV3PSIsIml2UGFyYW1ldGVyU3BlYyI6IlRQUlZQd1ZLdGRqWkdVdWkiLCJtYXRlcmlhbFNldFNlcmlhbCI6MX0%3D&branch=master
  :target: https://us-east-2.console.aws.amazon.com/codesuite/codebuild/projects/StepFunctionsPythonSDK-unittests-private/history?region=us-east-2
  :alt: Unit Tests Build Status

.. |readthedocs| image:: https://readthedocs.org/projects/aws-step-functions-data-science-sdk/badge/?version=latest
  :target: https://aws-step-functions-data-science-sdk.readthedocs.io/en/latest/?badge=latest
  :alt: Documentation Status

.. |pypi| image:: https://img.shields.io/pypi/v/stepfunctions
  :target: https://pypi.org/project/stepfunctions/
  :alt: PyPI
