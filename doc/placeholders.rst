Placeholders
=============

Once defined, a workflow is static unless you update it explicitly. But, you can pass
input to workflow executions. You can have dynamic values
that you use in the **parameters** fields of the steps in your workflow. For this,
the AWS Step Functions Data Science SDK provides a way to define placeholders to pass around when you
create your workflow. There are 2 mechanisms for passing dynamic values in a workflow.

The first mechanism is a global input to the workflow execution. This input is
accessible to all the steps in the workflow. The SDK provides :py:meth:`stepfunctions.inputs.ExecutionInput`
to define the schema for this input, and to access the values in your workflow.

.. code-block:: python

  # Create an instance of ExecutionInput class, and define a schema. Defining
  # a schema is optional, but it is a good practice

  my_execution_input = ExecutionInput(schema={
      'myDynamicInput': str
  })

  lambda_state = LambdaStep(
      state_id="MyLambdaStep",
      parameters={
          "FunctionName": "MyLambda",
          "Payload": {
             "input": my_execution_input["myDynamicInput"] #Use as a
                                                           #Python dictionary
          }
      }
  )

  # Workflow is created with the placeholders
  workflow = Workflow(
      name='MyLambdaWorkflowWithGlobalInput',
      definition=lambda_state,
      role=workflow_execution_role,
      execution_input=my_execution_input # Provide the execution_input when
                                         # defining your workflow
  )

  # Create the workflow on AWS Step Functions
  workflow.create()

  # The placeholder is assigned a value during execution. The SDK will
  # verify that all placeholder values are assigned values, and that
  # these values are of the expected type based on the defined schema
  # before the execution starts.

  workflow.execute(inputs={'myDynamicInput': "WorldHello"})

The second mechanism is for passing dynamic values from one step to the next
step. The output of one step becomes the input of the next step.
The SDK provides the :py:meth:`stepfunctions.inputs.StepInput` class for this.

By default, each step has an output method :py:meth:`stepfunctions.steps.states.State.output`
that returns the placeholder output for that step.

.. code-block:: python

  lambda_state_first = LambdaStep(
      state_id="MyFirstLambdaStep",
      parameters={
          "FunctionName": "MakeApiCall",
          "Payload": {
            "input": "20192312"
            }
          }
        )

  lambda_state_second = LambdaStep(
        state_id="MySecondLambdaStep",
        parameters={
          "FunctionName": "ProcessCallResult",
          "Payload": {
            "input": lambda_state_first.output()["Response"] #Use as a Python dictionary
            }
          }
        )

  definition = Chain([lambda_state_first, lambda_state_second])



.. autoclass:: stepfunctions.inputs.Placeholder

.. autoclass:: stepfunctions.inputs.ExecutionInput
                :inherited-members:

.. autoclass:: stepfunctions.inputs.StepInput
                :inherited-members:
