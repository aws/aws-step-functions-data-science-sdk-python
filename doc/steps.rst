
###########################
Steps
###########################

Steps are the basic building block of workflows in the AWS Step Functions Data
Science SDK. Once you create steps, you chain them together to create a workflow,
create that workflow in AWS Step Functions, and execute the workflow in the
AWS cloud.

Step Functions creates workflows out of steps called `States <https://docs.aws.amazon.com/step-functions/latest/dg/concepts-states.html>`__,
and expresses that workflow in the `Amazon States Language <https://docs.aws.amazon.com/step-functions/latest/dg/concepts-amazon-states-language.html>`__.
When you create a workflow in the AWS Step Functions Data Science SDK, it
creates a State Machine representing your workflow and steps in AWS Step
Functions.

.. toctree::
    :maxdepth: 2

    states
    choicerules
    compute
    sagemaker
    services
