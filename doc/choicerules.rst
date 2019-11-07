Choice Rules
=============

This module defines the `choice rules <https://docs.aws.amazon.com/step-functions/latest/dg/amazon-states-language-choice-state.html#amazon-states-language-choice-state-rules>`__ for a Choice state. 

Use the :py:meth:`~stepfunctions.steps.Choice.add_choice` method to add a branch to a Choice step. 

.. code-block:: python

    my_choice_state.add_choice(
        rule=ChoiceRule.BooleanEquals(variable=previous_state.output()["Success"], value=True),
        next_step=happy_path
    )
    my_choice_state.add_choice(
        ChoiceRule.BooleanEquals(variable=previous_state.output()["Success"], value=False),
        next_step=sad_state
    )


In this example, choice rules are added to the Choice state
``my_choice_state`` using :py:meth:`~stepfunctions.steps.Choice.add_choice`.
Logic in a `Choice state <https://docs.aws.amazon.com/step-functions/latest/dg/amazon-states-language-choice-state.html>`__ 
is implemented with the help of Choice Rules. A Choice Rule encapsulates a 
comparison, which contains the following: 

- An input **variable** to compare
- The **type** of comparison
- The **value** to compare the variable to

The type of comparison is abstracted by the classes provided in this module. Multiple choice rules can be 
compounded together using the :py:meth:`~stepfunctions.steps.choice_rule.ChoiceRule.And` or 
:py:meth:`~stepfunctions.steps.choice_rule.ChoiceRule.Or` classes. A choice rule can be negated using 
the :py:meth:`~stepfunctions.steps.choice_rule.ChoiceRule.Not` class.

.. autoclass:: stepfunctions.steps.choice_rule.BaseRule

.. autoclass:: stepfunctions.steps.choice_rule.Rule

.. autoclass:: stepfunctions.steps.choice_rule.CompoundRule

.. autoclass:: stepfunctions.steps.choice_rule.NotRule

.. autoclass:: stepfunctions.steps.choice_rule.ChoiceRule
