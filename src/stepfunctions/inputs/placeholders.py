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

import collections
import json

from stepfunctions.inputs.utils import flatten, replace_type_with_str

ValidationResult = collections.namedtuple('ValidationResult', 'valid keys_missing keys_type_mismatch')


class Placeholder(object):

    """
    A collection of Placeholder variables.
    """

    def __init__(self, schema=None, **kwargs):
        """
        Args:
            schema (dict, optional): Schema for the placeholder collection. (default: None)
                                     Example below::
                                        {
                                            'ModelName': str,
                                            'JobName': str,
                                            'Hyperparameters': {
                                                'tol': float
                                            }
                                        }

        Keyword Args:
            name (str, optional): Name of the placeholder variable. (default: None)
            type (type, optional): Type of the placeholder variable. (default: None)
            parent (Placeholder, optional): Parent variable for a placeholder variable. (default: None)
        """
        self.store = {}
        self.immutable = False
        self.schema = schema
        if self.schema:
            self._set_schema(schema)
            self._make_immutable()
        self.json_str_template = "{}"
        
        self.name = kwargs.get("name")
        self.type = kwargs.get("type")
        self.parent = kwargs.get("parent")
        

    def get(self, name, type):
        """
        Create a placeholder variable with an associated type.

        Args:
            name (str): Name of the placeholder variable.
            type (type): Type of the placeholder variable.
        
        Raises:
            ValueError: If placeholder variable with the same name but different type already exists.
            ValueError: If placeholder variable does not fit into a previously specified schema for the placeholder collection.
        
        Returns:
            Placeholder: Placeholder variable.
        """
        if not self._is_valid_name(name):
            raise ValueError('Key name can only be string or integer')
        if name in self.store:
            curr_variable = self.store[name]
            if curr_variable.type != type:
                raise ValueError('Key already exists with a different value type: {current_value_type}'.format(current_value_type=curr_variable.type))
            return curr_variable
        else:
            self.store[name] = self._create_variable(name=name, parent=self, type=type)
            return self.store[name]

    def get_schema_as_dict(self):
        """
        Generate a schema for the placeholder collection as a Python dictionary.

        Returns:
            dict: Placeholder collection schema.
        """
        schema = {}
        for k, v in self.store.items():
            if v._is_empty():
                schema[k] = v.type or str
            else:
                schema[k] = v.get_schema_as_dict()
        return schema

    def get_schema_as_json(self, pretty=False):
        """
        Generate a schema for the placeholder collection as a JSON formatted string.

        Args:
            pretty (bool, optional): Boolean flag set to `True` if JSON string should be prettified. `False`, otherwise. (default: False)

        Returns:
            str: JSON formatted string representation of the block.
        """
        dict_schema_str = replace_type_with_str(self.get_schema_as_dict())

        if pretty:
            return json.dumps(dict_schema_str, indent=4)

        return json.dumps(dict_schema_str)

    def contains(self, placeholder):
        """
        Check if the placeholder collection contains the specified placeholder variable.

        Args:
            placeholder (Placeholder): Placeholder variable to search for, in the collection.

        Returns:
            bool: `True` if placeholder variable was found in the collection. `False`, otherwise.
        """
        for k, v in self.store.items():
            if placeholder == v:
                return True
            elif v.contains(placeholder):
                return True
        return False

    def __contains__(self, placeholder):
        """
            Containment check operator for placeholder variables.
        """
        return self.contains(placeholder)

    def validate(self, input):
        """
        Validate a specified input against the placeholder collection schema.

        Args:
            input (dict): Input to validate against the placeholder collection schema.

        Returns:
            ValidationResult: Named tuple with the keys:
                                `valid` (Boolean): Representing the result of validation ,
                                `keys_missing` (list(str)): List of keys missing in the input ,
                                `keys_type_mismatch` (list(str), type, type): List of tuples with key name, expected type, and provided type.
        """
        if input is None:
            return False, None, None
        flattened_schema = flatten(self.get_schema_as_dict())
        flattened_input = flatten(input)
        keys_missing = [i for i in flattened_schema if i not in flattened_input]
        keys_type_mismatch = []
        for k, v in flattened_input.items():
            if k in flattened_schema and not isinstance(v, flattened_schema.get(k)):
                keys_type_mismatch.append((k, flattened_schema.get(k), type(v)))
        if len(keys_missing) > 0 or len(keys_type_mismatch) > 0:
            valid = False
        else:
            valid = True
        return ValidationResult(valid=valid, keys_missing=keys_missing, keys_type_mismatch=keys_type_mismatch)

    def _create_variable(self, name, parent, type=None):
        raise NotImplementedError

    def _get_path(self):
        """
            Get path to a placeholder variable node in the collection.
        """
        path = []
        node = self
        while node.name is not None:
            path.append(node.name)
            node = node.parent
        path.reverse()
        return path

    def _is_empty(self):
        """
            Check if the store for a placeholder collection/variable is empty.
        """
        return len(self.store) == 0

    def _set_schema(self, schema, path=[]):
        """
            Set the schema for a placeholder collection.
        """
        for k, v in schema.items():
            if isinstance(v, dict):
                self._set_schema(v, path + [k])
            else:
                current = self
                for node in path:
                    current = current.get(node, dict)
                temp = current.get(k, v)

    def _make_immutable(self):
        """
            Make a placeholder collection (including all variables contained) immutable.
        """
        for k, v in self.store.items():
            if isinstance(v, Placeholder):
                v._make_immutable()
        self.immutable = True


    def _is_valid_name(self, name):
        if isinstance(name, str) or isinstance(name, int):
            return True
        else:
            return False

    def __getitem__(self, name):
        """
            Subscript operator to build placeholder variables.
        """
        if not self._is_valid_name(name):
            raise ValueError('Key name can only be string or integer')
        if name in self.store:
            return self.store[name]
        else:
            self.store[name] = self._create_variable(name=name, parent=self)
            return self.store[name]

    def _join_path(self, path):
        subscript_list = []
        for i in path:
            if isinstance(i, str):
                subscript_list.append("['{}']".format(i))
            elif isinstance(i, int):
                subscript_list.append('[{}]'.format(i))
        return "".join(subscript_list)

    def to_jsonpath(self):
        """
        Returns a JSON path representation of the placeholder variable to be used for step parameters.
        
        Returns:
            str: JSON path representation of the placeholder variable
        """
        return self.json_str_template.format(self._join_path(self._get_path()))


class ExecutionInput(Placeholder):

    """
        Top-level class for execution input placeholders.
    """
    
    def __init__(self, schema=None, **kwargs):
        super(ExecutionInput, self).__init__(schema, **kwargs)
        self.json_str_template = '$$.Execution.Input{}'

    def _create_variable(self, name, parent, type=None):
        """
            Creates a placeholder variable for Workflow Input.
            A placeholder variable can only be created if the collection is not immutable due to a pre-specified schema.
        """
        if self.immutable:
            raise ValueError("Placeholder variable does not conform to schema set for the placeholder collection.")
        if type:
            return ExecutionInput(name=name, parent=parent, type=type)
        else:
            return ExecutionInput(name=name, parent=parent)
    

class StepInput(Placeholder):

    """
        Top-level class for step input placeholders.
    """

    def __init__(self, schema=None, **kwargs):
        super(StepInput, self).__init__(schema, **kwargs)
        self.json_str_template = '${}'
        
    def _create_variable(self, name, parent, type=None):
        """
            Creates a placeholder variable for Step Input.
            A placeholder variable can only be created if the collection is not immutable due to a pre-specified schema.
        """
        if self.immutable:
            raise ValueError("Placeholder variable does not conform to schema set for the placeholder collection.")
        if type:
            return StepInput(name=name, parent=parent, type=type)
        else:
            return StepInput(name=name, parent=parent)
