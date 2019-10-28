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

from stepfunctions.inputs import StepInput

VALIDATORS = {
    'String': (str,),
    'Numeric': (int, float),
    'Boolean': (bool,),
    'Timestamp': (str,),
}


class BaseRule(object):

    """
    Abstract class for rules.
    """

    def to_dict(self):
        return {}
    
    def __repr__(self):
        return '{}()'.format(self.__class__.__name__)
    
    def __str__(self):
        return '{}'.format(self.to_dict())


class Rule(BaseRule):

    """
    Class for creating a rule.
    """

    def __init__(self, variable, operator, value):
        """
        Args:
            variable (str): Path to the variable to compare.
            operator (str): Comparison operator to be applied. 
            value (type depends on *operator*): Constant value to compare `variable` against. 
        
        Raises:
            ValueError: If `variable` doesn't start with '$'
            ValueError: If `value` is not the appropriate datatype for the `operator` specified.
        """
        # Validate the variable name
        if not isinstance(variable, StepInput) and not variable.startswith('$'):
            raise ValueError("Expected variable must be a placeholder or must start with '$', but got '{variable}'".format(variable=variable))
        
        # Validate the variable value
        for k, v in VALIDATORS.items():
            if operator.startswith(k) and not isinstance(value, v):
                raise ValueError('Expected value to be a {type}, but got {value}'.format(type=k, value=value))

        self.variable = variable
        self.operator = operator
        self.value = value
    
    def to_dict(self):
        if isinstance(self.variable, StepInput):
            result = { 'Variable': self.variable.to_jsonpath() }
        else:
            result = { 'Variable': self.variable }
        result[self.operator] = self.value
        return result
    
    def __repr__(self):
        return '{}(variable={!r}, operator={!r}, value={!r})'.format(
            self.__class__.__name__,
            self.variable, self.operator, self.value
        )


class CompoundRule(BaseRule):

    """
    Class for creating a compound rule.
    """

    def __init__(self, operator, rules):
        """
        Args:
            operator (str): Compounding operator to be applied.
            rules (list(BaseRule)): List of rules to compound together.
        
        Raises:
            ValueError: If any item in the `rules` list is not a BaseRule object.
        """
        for rule in rules:
            if not isinstance(rule, BaseRule):
                raise ValueError("Rule '{rule}' is invalid".format(rule=rule))
        
        self.operator = operator
        self.rules = rules
    
    def to_dict(self):
        return { self.operator: [ rule.to_dict() for rule in self.rules ] }
    
    def __repr__(self):
        return '{}(operator={!r}, rules={!r})'.format(
            self.__class__.__name__,
            self.operator, self.rules
        )


class NotRule(BaseRule):

    """
    Class for creating a negation rule.
    """

    def __init__(self, rule):
        """
        Args:
            rules (BaseRule): Rule to negate.
        
        Raises:
            ValueError: If `rule` is not a BaseRule object.
        """
        if not isinstance(rule, BaseRule):
            raise ValueError("Rule '{rule}' is invalid".format(rule=rule))
        
        self.rule = rule
    
    def to_dict(self):
        return {
            'Not': self.rule.to_dict()
        }
    
    def __repr__(self):
        return '{}(rule={!r})'.format(
            self.__class__.__name__,
            self.rule
        )


class ChoiceRule(object):

    """
    Factory class for creating a choice rule.
    """
    
    @classmethod
    def StringEquals(cls, variable, value):
        """
        Creates a rule with the `StringEquals` operator.

        Args:
            variable (str): Path to the variable to compare.
            value (str): Constant value to compare `variable` against.

        Returns:
            Rule: Rule with `StringEquals` operator.
        """
        return Rule(variable, 'StringEquals', value)
    
    @classmethod
    def StringLessThan(cls, variable, value):
        """
        Creates a rule with the `StringLessThan` operator.

        Args:
            variable (str): Path to the variable to compare.
            value (str): Constant value to compare `variable` against.

        Returns:
            Rule: Rule with `StringLessThan` operator.
        """
        return Rule(variable, 'StringLessThan', value)

    @classmethod
    def StringGreaterThan(cls, variable, value):
        """
        Creates a rule with the `StringGreaterThan` operator.

        Args:
            variable (str): Path to the variable to compare.
            value (str): Constant value to compare `variable` against.

        Returns:
            Rule: Rule with `StringGreaterThan` operator.
        """
        return Rule(variable, 'StringGreaterThan', value)

    @classmethod
    def StringLessThanEquals(cls, variable, value):
        """
        Creates a rule with the `StringLessThanEquals` operator.

        Args:
            variable (str): Path to the variable to compare.
            value (str): Constant value to compare `variable` against.

        Returns:
            Rule: Rule with `StringLessThanEquals` operator.
        """
        return Rule(variable, 'StringLessThanEquals', value)

    @classmethod
    def StringGreaterThanEquals(cls, variable, value):
        """
        Creates a rule with the `StringGreaterThanEquals` operator.

        Args:
            variable (str): Path to the variable to compare.
            value (str): Constant value to compare `variable` against.

        Returns:
            Rule: Rule with `StringGreaterThanEquals` operator.
        """
        return Rule(variable, 'StringGreaterThanEquals', value)

    @classmethod
    def NumericEquals(cls, variable, value):
        """
        Creates a rule with the `NumericEquals` operator.

        Args:
            variable (str): Path to the variable to compare.
            value (int): Constant value to compare `variable` against.

        Returns:
            Rule: Rule with `NumericEquals` operator.
        """
        return Rule(variable, 'NumericEquals', value)

    @classmethod
    def NumericLessThan(cls, variable, value):
        """
        Creates a rule with the `NumericLessThan` operator.

        Args:
            variable (str): Path to the variable to compare.
            value (int): Constant value to compare `variable` against.

        Returns:
            Rule: Rule with `NumericLessThan` operator.
        """
        return Rule(variable, 'NumericLessThan', value)

    @classmethod
    def NumericGreaterThan(cls, variable, value):
        """
        Creates a rule with the `NumericGreaterThan` operator.

        Args:
            variable (str): Path to the variable to compare.
            value (int): Constant value to compare `variable` against.

        Returns:
            Rule: Rule with `NumericGreaterThan` operator.
        """
        return Rule(variable, 'NumericGreaterThan', value)

    @classmethod
    def NumericLessThanEquals(cls, variable, value):
        """
        Creates a rule with the `NumericLessThanEquals` operator.

        Args:
            variable (str): Path to the variable to compare.
            value (int): Constant value to compare `variable` against.

        Returns:
            Rule: Rule with `NumericLessThanEquals` operator.
        """
        return Rule(variable, 'NumericLessThanEquals', value)

    @classmethod
    def NumericGreaterThanEquals(cls, variable, value):
        """
        Creates a rule with the `NumericGreaterThanEquals` operator.

        Args:
            variable (str): Path to the variable to compare.
            value (int): Constant value to compare `variable` against.

        Returns:
            Rule: Rule with `NumericGreaterThanEquals` operator.
        """
        return Rule(variable, 'NumericGreaterThanEquals', value)

    @classmethod
    def BooleanEquals(cls, variable, value):
        """
        Creates a rule with the `BooleanEquals` operator.

        Args:
            variable (str): Path to the variable to compare.
            value (bool): Constant value to compare `variable` against.

        Returns:
            Rule: Rule with `BooleanEquals` operator.
        """
        return Rule(variable, 'BooleanEquals', value)

    @classmethod
    def TimestampEquals(cls, variable, value):
        """
        Creates a rule with the `TimestampEquals` operator.

        Args:
            variable (str): Path to the variable to compare.
            value (str): Constant value to compare `variable` against.

        Returns:
            Rule: Rule with `TimestampEquals` operator.
        """
        return Rule(variable, 'TimestampEquals', value)

    @classmethod
    def TimestampLessThan(cls, variable, value):
        """
        Creates a rule with the `TimestampLessThan` operator.

        Args:
            variable (str): Path to the variable to compare.
            value (str): Constant value to compare `variable` against.

        Returns:
            Rule: Rule with `TimestampLessThan` operator.
        """
        return Rule(variable, 'TimestampLessThan', value)

    @classmethod
    def TimestampGreaterThan(cls, variable, value):
        """
        Creates a rule with the `TimestampGreaterThan` operator.

        Args:
            variable (str): Path to the variable to compare.
            value (str): Constant value to compare `variable` against.

        Returns:
            Rule: Rule with `TimestampGreaterThan` operator.
        """
        return Rule(variable, 'TimestampGreaterThan', value)

    @classmethod
    def TimestampLessThanEquals(cls, variable, value):
        """
        Creates a rule with the `TimestampLessThanEquals` operator.

        Args:
            variable (str): Path to the variable to compare.
            value (str): Constant value to compare `variable` against.

        Returns:
            Rule: Rule with `TimestampLessThanEquals` operator.
        """
        return Rule(variable, 'TimestampLessThanEquals', value)

    @classmethod
    def TimestampGreaterThanEquals(cls, variable, value):
        """
        Creates a rule with the `TimestampGreaterThanEquals` operator.

        Args:
            variable (str): Path to the variable to compare.
            value (str): Constant value to compare `variable` against.

        Returns:
            Rule: Rule with `TimestampGreaterThanEquals` operator.
        """
        return Rule(variable, 'TimestampGreaterThanEquals', value)

    @classmethod
    def And(cls, rules):
        """
        Creates a compound rule with the `And` operator.

        Args:
            rules (list(BaseRule)): List of rules to compound together.

        Returns:
            CompoundRule: Compound rule with `And` operator.
        """
        return CompoundRule('And', rules)
    
    @classmethod
    def Or(cls, rules):
        """
        Creates a compound rule with the `Or` operator.

        Args:
            rules (list(BaseRule)): List of rules to compound together.

        Returns:
            CompoundRule: Compound rule with `Or` operator.
        """
        return CompoundRule('Or', rules)
    
    @classmethod
    def Not(cls, rule):
        """
        Creates a negation for a rule.

        Args:
            rule (BaseRule): Rule to Negate.

        Returns:
            NotRule: Rule with `Not` operator.
        """
        return NotRule(rule)
