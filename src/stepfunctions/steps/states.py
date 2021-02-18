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

import json
import logging

from stepfunctions.exceptions import DuplicateStatesInChain
from stepfunctions.steps.fields import Field
from stepfunctions.inputs import ExecutionInput, StepInput


logger = logging.getLogger('stepfunctions.states')


def to_pascalcase(text):
    return ''.join([t.title() for t in text.split('_')])


class Block(object):

    """
    Base class to abstract blocks used in `Amazon States Language <https://states-language.net/spec.html>`_.
    """

    def __init__(self, **kwargs):
        self.fields = kwargs
        for k, v in self.fields.items():
            if not self.is_field_allowed(k):
                raise TypeError("Field '{field}' is not supported.".format(field=k))

    def __getattr__(self, name):
        return self.fields.get(name, None)

    def is_field_allowed(self, field_name):
        return field_name in [field.value for field in self.allowed_fields()]

    def allowed_fields(self):
        return []

    def _replace_placeholders(self, params):
        if not isinstance(params, dict):
            return params
        modified_parameters = {}
        for k, v in params.items():
            if isinstance(v, (ExecutionInput, StepInput)):
                modified_key = "{key}.$".format(key=k)
                modified_parameters[modified_key] = v.to_jsonpath()
            elif isinstance(v, dict):
                modified_parameters[k] = self._replace_placeholders(v)
            elif isinstance(v, list):
                modified_parameters[k] = [self._replace_placeholders(i) for i in v]
            else:
                modified_parameters[k] = v
        return modified_parameters

    def to_dict(self):
        result = {}
        fields_accepted_as_none = ('result_path', 'input_path', 'output_path')
        # Common fields
        for k, v in self.fields.items():
            if v is not None or k in fields_accepted_as_none:
                k = to_pascalcase(k)
                if k == to_pascalcase(Field.Parameters.value):
                    result[k] = self._replace_placeholders(v)
                else:
                    result[k] = v

        return result

    def to_json(self, pretty=False):
        """Serialize to a JSON formatted string.

        Args:
            pretty (bool, optional): Boolean flag set to `True` if JSON string should be prettified. `False`, otherwise. (default: False)

        Returns:
            str: JSON formatted string representation of the block.
        """
        if pretty:
            return json.dumps(self.to_dict(), indent=4)

        return json.dumps(self.to_dict())

    def __repr__(self):
        return '{}({})'.format(
           self.__class__.__name__,
           ', '.join(['{}={!r}'.format(k, v) for k, v in self.fields.items()])
        )

    def __str__(self):
        return self.to_json(pretty=True)


class Retry(Block):

    """
    A class for creating a Retry block.
    """

    def __init__(self, **kwargs):
        """Initialize a Retry block.

        Args:
            error_equals (list(str)): Non-empty list of strings, which match `Error Names <https://states-language.net/spec.html#error-names>`_. When a state reports an error, the interpreter scans through the retriers and, when the Error Name appears in the value of of a retrier’s `error_equals` field, implements the retry policy described in that retrier.
            interval_seconds (int, optional): Positive integer representing the number of seconds before the first retry attempt. (default: 1)
            max_attempts (int, optional): Non-negative integer representing the maximum number of retry attempts. (default: 3)
            backoff_rate(float, optional): A number which is the multiplier that increases the retry interval on each attempt. (default: 2.0)
        """
        super(Retry, self).__init__(**kwargs)

    def allowed_fields(self):
        return [
            Field.ErrorEquals,
            Field.IntervalSeconds,
            Field.MaxAttempts,
            Field.BackoffRate
        ]


class Catch(Block):

    """
    A class for creating a Catch block.
    """

    def __init__(self, next_step, **kwargs):
        """Initialize a Catch block.

        Args:
            error_equals (list(str)): Non-empty list of strings, which match `Error Names <https://states-language.net/spec.html#error-names>`_. When a state reports an error, the interpreter scans through the catchers and, when the Error Name appears in the value of of a catcher's `error_equals` field, transitions to the `next_step` described in the catcher.
            next_step (State or Chain): Next state or chain to transition to.
        """
        super(Catch, self).__init__(**kwargs)
        self.next_step = next_step

    def allowed_fields(self):
        return [
            Field.ErrorEquals,
            Field.ResultPath
        ]

    def to_dict(self):
        result = super(Catch, self).to_dict()
        result[Field.Next.name] = self.next_step.state_id
        return result


class State(Block):

    """
    Base class to abstract states in `Amazon States Language <https://states-language.net/spec.html>`_.
    """

    def __init__(self, state_id, state_type, output_schema=None, **kwargs):
        """
        Args:
            state_id (str): State name whose length **must be** less than or equal to 128 unicode characters. State names **must be** unique within the scope of the whole state machine.
            state_type (str): Type of the state. (Allowed values: `'Pass'`, `'Succeed'`, `'Fail'`, `'Wait'`, `'Task'`, `'Choice'`, `'Parallel'`, `'Map'`).
            output_schema (dict): Expected output schema for the State. This is used to validate placeholder inputs used by the next state in the state machine. (default: None)
            comment (str, optional): Human-readable comment or description. (default: None)
            input_path (str, optional): Path applied to the state’s raw input to select some or all of it; that selection is used by the state. (default: '$')
            parameters (dict, optional): The value of this field becomes the effective input for the state.
            result_path (str, optional): Path specifying the raw input’s combination with or replacement by the state’s result. (default: '$')
            output_path (str, optional): Path applied to the state’s output after the application of `result_path`, producing the effective output which serves as the raw input for the next state. (default: '$')
        """
        super(State, self).__init__(**kwargs)
        self.fields['type'] = state_type

        self.state_type = state_type
        self.state_id = state_id
        self.output_schema = output_schema
        self.step_output = StepInput(schema=output_schema)
        self.retries = []
        self.catches = []
        self.next_step = None
        self.in_chain = None

    def __repr__(self):
        return self.state_id + ' ' + super(State, self).__repr__()

    def allowed_fields(self):
        return [
            Field.Comment,
            Field.InputPath,
            Field.OutputPath,
            Field.Parameters,
            Field.ResultPath
        ]

    def update_parameters(self, params):
        """
        Update `parameters` field in the state, if supported.

        Args:
            params (dict or list): The value of this field becomes the effective input for the state.
        """
        if Field.Parameters in self.allowed_fields():
            self.fields[Field.Parameters.value] = params

    def next(self, next_step):
        """
        Specify the next state or chain to transition to.

        Args:
            next_step (State or Chain): Next state or chain to transition to.

        Returns:
            State or Chain: Next state or chain that will be transitioned to.
        """
        if self.type in ('Choice', 'Succeed', 'Fail'):
            raise ValueError('Unexpected State instance `{step}`, State type `{state_type}` does not support method `next`.'.format(step=next_step, state_type=self.type))

        self.next_step = next_step
        return self.next_step

    def output(self):
        """
        Get the placeholder collection for the State's output.

        Returns:
            StepInput: Placeholder collection representing the State's output, and consequently the input to the next state in the workflow (if one exists).
        """
        return self.step_output

    def accept(self, visitor):
        if visitor.is_visited(self):
            return

        visitor.visit(self)
        if self.next_step is not None:
            self.next_step.accept(visitor)
        for catch in self.catches:
            catch.next_step.accept(visitor)

    def add_retry(self, retry):
        """
        Add a Retry block to the tail end of the list of retriers for the state.

        Args:
            retry (Retry): Retry block to add.
        """
        if Field.Retry in self.allowed_fields():
            self.retries.append(retry)
        else:
            raise ValueError("{state_type} state does not support retry field. ".format(state_type=type(self).__name__))

    def add_catch(self, catch):
        """
        Add a Catch block to the tail end of the list of catchers for the state.

        Args:
            catch (Catch): Catch block to add.
        """
        if Field.Catch in self.allowed_fields():
            self.catches.append(catch)
        else:
            raise ValueError("{state_type} state does not support catch field. ".format(state_type=type(self).__name__))

    def to_dict(self):
        result = super(State, self).to_dict()

        # Next step
        if self.next_step is not None:
            result[Field.Next.name] = self.next_step.state_id
        elif self.state_type not in ('Succeed', 'Fail', 'Choice'):
            result[Field.End.name] = True

        # Retry and catch
        if self.retries and self.is_field_allowed(Field.Retry.value):
            result[Field.Retry.name] = [retry.to_dict() for retry in self.retries]
        if self.catches and self.is_field_allowed(Field.Catch.value):
            result[Field.Catch.name] = [catch.to_dict() for catch in self.catches]

        return result

class Pass(State):

    """
    Pass State simply passes its input to its output, performing no work. Pass States are useful when constructing and debugging state machines.
    """

    def __init__(self, state_id, **kwargs):
        """
        Args:
            state_id (str): State name whose length **must be** less than or equal to 128 unicode characters. State names **must be** unique within the scope of the whole state machine.
            comment (str, optional): Human-readable comment or description. (default: None)
            input_path (str, optional): Path applied to the state’s raw input to select some or all of it; that selection is used by the state. (default: '$')
            parameters (dict, optional): The value of this field becomes the effective input for the state.
            result_path (str, optional): Path specifying the raw input’s combination with or replacement by the state’s result. (default: '$')
            result (str, optional): If present, its value is treated as the output of a virtual task, and placed as prescribed by the `result_path` field, if any, to be passed on to the next state. If `result` is not provided, the output is the input.
            output_path (str, optional): Path applied to the state’s output after the application of `result_path`, producing the effective output which serves as the raw input for the next state. (default: '$')
        """

        super(Pass, self).__init__(state_id, 'Pass', **kwargs)

    def allowed_fields(self):
        return [
            Field.Comment,
            Field.InputPath,
            Field.OutputPath,
            Field.Parameters,
            Field.ResultPath,
            Field.Result
        ]


class Succeed(State):

    """
    Succeed State terminates a state machine successfully. The Succeed State is a useful target for  :py:class:`Choice`-state branches that don't do anything but terminate the machine.
    """

    def __init__(self, state_id, **kwargs):
        """
        Args:
            state_id (str): State name whose length **must be** less than or equal to 128 unicode characters. State names **must be** unique within the scope of the whole state machine.
            comment (str, optional): Human-readable comment or description. (default: None)
            input_path (str, optional): Path applied to the state’s raw input to select some or all of it; that selection is used by the state. (default: '$')
            output_path (str, optional): Path applied to the state’s output, producing the effective output which serves as the raw input for the next state. (default: '$')
        """
        super(Succeed, self).__init__(state_id, 'Succeed', **kwargs)

    def allowed_fields(self):
        return [
            Field.Comment,
            Field.InputPath,
            Field.OutputPath
        ]


class Fail(State):

    """
    Fail State terminates the machine and marks it as a failure.
    """

    def __init__(self, state_id, **kwargs):
        """
        Args:
            state_id (str): State name whose length **must be** less than or equal to 128 unicode characters. State names **must be** unique within the scope of the whole state machine.
            error (str): Error name that can be used for error handling (retry/catch), operational, or diagnostic purposes.
            cause (str): Human-readable message describing the cause of the failure/error.
            comment (str, optional): Human-readable comment or description. (default: None).
        """
        super(Fail, self).__init__(state_id, 'Fail', **kwargs)

    def allowed_fields(self):
        return [
            Field.Comment,
            Field.Error,
            Field.Cause
        ]


class Wait(State):

    """
    Wait state causes the interpreter to delay the machine from continuing for a specified time. The time can be specified as a wait duration, specified in seconds, or an absolute expiry time, specified as an ISO-8601 extended offset date-time format string.
    """

    def __init__(self, state_id, **kwargs):
        """
        The Wait state **must contain exactly one** of `seconds`, `seconds_path`, `timestamp`, or `timestamp_path`.

        Args:
            state_id (str): State name whose length **must be** less than or equal to 128 unicode characters. State names **must be** unique within the scope of the whole state machine.
            seconds (int): Wait duration specified in seconds.
            seconds_path (str): Path applied to the state's input to select the wait duration in seconds.
            timestamp (str): Absolute expiry time, specified as an ISO-8601 extended offset date-time format string.
            timestamp_path (str): Path applied to the state's input to select the timestamp to be used for wait duration.
            comment (str, optional): Human-readable comment or description. (default: None)
            input_path (str, optional): Path applied to the state’s raw input to select some or all of it; that selection is used by the state. (default: '$')
            output_path (str, optional): Path applied to the state’s output, producing the effective output which serves as the raw input for the next state. (default: '$')
        """
        super(Wait, self).__init__(state_id, 'Wait', **kwargs)
        if len([v for v in (self.seconds, self.timestamp, self.timestamp_path, self.seconds_path) if v is not None]) != 1:
            raise ValueError("The Wait state MUST contain exactly one of 'seconds', 'seconds_path', 'timestamp' or 'timestamp_path'.")

    def allowed_fields(self):
        return [
            Field.Comment,
            Field.InputPath,
            Field.OutputPath,
            Field.Seconds,
            Field.Timestamp,
            Field.SecondsPath,
            Field.TimestampPath
        ]


class Choice(State):

    """
    Choice state adds branching logic to a state machine. The state holds a list of *rule* and *next_step* pairs. The interpreter attempts pattern-matches against the rules in list order and transitions to the state or chain specified in the *next_step* field on the first *rule* where there is an exact match between the input value and a member of the comparison-operator array.
    """

    def __init__(self, state_id, **kwargs):
        """
        Args:
            state_id (str): State name whose length **must be** less than or equal to 128 unicode characters. State names **must be** unique within the scope of the whole state machine.
            comment (str, optional): Human-readable comment or description. (default: None)
            input_path (str, optional): Path applied to the state’s raw input to select some or all of it; that selection is used by the state. (default: '$')
            output_path (str, optional): Path applied to the state’s output, producing the effective output which serves as the raw input for the next state. (default: '$')
        """
        super(Choice, self).__init__(state_id, 'Choice', **kwargs)
        self.choices = []
        self.default = None

    def allowed_fields(self):
        return [
            Field.Comment,
            Field.InputPath,
            Field.OutputPath
        ]

    def add_choice(self, rule, next_step):
        """Add a *rule*, *next_step* pair to the choice state.

        Args:
            rule (:py:class:`stepfunctions.steps.choice_rule.BaseRule`): Rule to pattern match the input against.
            next_step (State or Chain): Next state or chain to transition to, if `rule` is matches with the input.
        """
        self.choices.append([rule, next_step])

    def default_choice(self, next_step):
        """Add a default step to the choice state.

        The default step executes if none of the specified rules match.

        Args:
            next_step (State or Chain): Next state or chain to transition to, if none of the specified rules match.
        """
        self.default = next_step

    def to_dict(self):
        result = super(Choice, self).to_dict()

        serialized_choices = []
        for (rule, next_step) in self.choices:
            serialized_choice = rule.to_dict()
            serialized_choice[Field.Next.name] = next_step.state_id
            serialized_choices.append(serialized_choice)
        result[Field.Choices.name] = serialized_choices

        if self.default is not None:
            result[Field.Default.name] = self.default.state_id

        return result

    def accept(self, visitor):
        if visitor.is_visited(self):
            return

        visitor.visit(self)
        if self.default is not None:
            self.default.accept(visitor)

        for _, next_step in self.choices:
            next_step.accept(visitor)


class Parallel(State):

    """
    Parallel State causes parallel execution of "branches".

    A Parallel state causes the interpreter to execute each branch as concurrently as possible, and wait until each branch terminates (reaches a terminal state) before processing the next state in the Chain.
    """

    def __init__(self, state_id, **kwargs):
        """
        Args:
            state_id (str): State name whose length **must be** less than or equal to 128 unicode characters. State names **must be** unique within the scope of the whole state machine.
            comment (str, optional): Human-readable comment or description. (default: None)
            input_path (str, optional): Path applied to the state’s raw input to select some or all of it; that selection is used by the state. (default: '$')
            parameters (dict, optional): The value of this field becomes the effective input for the state.
            result_path (str, optional): Path specifying the raw input’s combination with or replacement by the state’s result. (default: '$')
            output_path (str, optional): Path applied to the state’s output after the application of `result_path`, producing the effective output which serves as the raw input for the next state. (default: '$')
        """
        super(Parallel, self).__init__(state_id, 'Parallel', **kwargs)
        self.branches = []

    def allowed_fields(self):
        return [
            Field.Comment,
            Field.InputPath,
            Field.OutputPath,
            Field.Parameters,
            Field.ResultPath,
            Field.Retry,
            Field.Catch
        ]

    def add_branch(self, branch):
        """
        Add a `State` or `Chain` as a branch to the Parallel state.

        Args:
            branch (State or Chain): State or Chain to attach as a branch to the Parallel state.
        """
        self.branches.append(branch)

    def to_dict(self):
        result = super(Parallel, self).to_dict()
        result[Field.Branches.name] = [
            Graph(branch).to_dict() for branch in self.branches
        ]
        return result


class Map(State):

    """
    Map state provides the ability to dynamically iterate over a state/subgraph for each entry in a list.

    A Map state can accept an input with a list of items, execute a state or chain for each item in the list, and return a list, with all corresponding results of each execution, as its output.
    """

    def __init__(self, state_id, **kwargs):
        """
        Args:
            state_id (str): State name whose length **must be** less than or equal to 128 unicode characters. State names **must be** unique within the scope of the whole state machine.
            iterator (State or Chain): State or chain to execute for each of the items in `items_path`.
            items_path (str, optional): Path in the input for items to iterate over. (default: '$')
            max_concurrency (int, optional): Maximum number of iterations to have running at any given point in time. (default: 0)
            comment (str, optional): Human-readable comment or description. (default: None)
            input_path (str, optional): Path applied to the state’s raw input to select some or all of it; that selection is used by the state. (default: '$')
            parameters (dict, optional): The value of this field becomes the effective input for the state.
            result_path (str, optional): Path specifying the raw input’s combination with or replacement by the state’s result. (default: '$')
            output_path (str, optional): Path applied to the state’s output after the application of `result_path`, producing the effective output which serves as the raw input for the next state. (default: '$')
        """
        super(Map, self).__init__(state_id, 'Map', **kwargs)

    def attach_iterator(self, iterator):
        """
        Attach `State` or `Chain` as iterator to the Map state, that will execute for each of the items in `items_path`. If an iterator was attached previously with the Map state, it will be replaced.

        Args:
            iterator (State or Chain): State or Chain to attach as iterator to the Map state.
        """
        self.iterator = iterator

    def allowed_fields(self):
        return [
            Field.Comment,
            Field.InputPath,
            Field.OutputPath,
            Field.Parameters,
            Field.ResultPath,
            Field.Retry,
            Field.Catch,
            Field.ItemsPath,
            Field.Iterator,
            Field.MaxConcurrency
        ]

    def to_dict(self):
        result = super(Map, self).to_dict()
        result[Field.Iterator.name] = Graph(self.iterator).to_dict()
        return result


class Task(State):

    """
    Task State causes the interpreter to execute the work identified by the state’s `resource` field.
    """

    def __init__(self, state_id, **kwargs):
        """
        Args:
            state_id (str): State name whose length **must be** less than or equal to 128 unicode characters. State names **must be** unique within the scope of the whole state machine.
            resource (str): A URI that uniquely identifies the specific task to execute. The States language does not constrain the URI scheme nor any other part of the URI.
            timeout_seconds (int, optional): Positive integer specifying timeout for the state in seconds. If the state runs longer than the specified timeout, then the interpreter fails the state with a `States.Timeout` Error Name. (default: 60)
            timeout_seconds_path (str, optional): Path specifying the state's timeout value in seconds from the state input. When resolved, the path must select a field whose value is a positive integer.
            heartbeat_seconds (int, optional): Positive integer specifying heartbeat timeout for the state in seconds. This value should be lower than the one specified for `timeout_seconds`. If more time than the specified heartbeat elapses between heartbeats from the task, then the interpreter fails the state with a `States.Timeout` Error Name.
            heartbeat_seconds_path (str, optional): Path specifying the state's heartbeat value in seconds from the state input. When resolved, the path must select a field whose value is a positive integer.
            comment (str, optional): Human-readable comment or description. (default: None)
            input_path (str, optional): Path applied to the state’s raw input to select some or all of it; that selection is used by the state. (default: '$')
            parameters (dict, optional): The value of this field becomes the effective input for the state.
            result_path (str, optional): Path specifying the raw input’s combination with or replacement by the state’s result. (default: '$')
            output_path (str, optional): Path applied to the state’s output after the application of `result_path`, producing the effective output which serves as the raw input for the next state. (default: '$')
        """
        super(Task, self).__init__(state_id, 'Task', **kwargs)
        if self.timeout_seconds is not None and self.timeout_seconds_path is not None:
            raise ValueError("Only one of 'timeout_seconds' or 'timeout_seconds_path' can be provided.")

        if self.heartbeat_seconds is not None and self.heartbeat_seconds_path is not None:
            raise ValueError("Only one of 'heartbeat_seconds' or 'heartbeat_seconds_path' can be provided.")

    def allowed_fields(self):
        return [
            Field.Comment,
            Field.InputPath,
            Field.OutputPath,
            Field.Parameters,
            Field.ResultPath,
            Field.TimeoutSeconds,
            Field.TimeoutSecondsPath,
            Field.HeartbeatSeconds,
            Field.HeartbeatSecondsPath,
            Field.Resource,
            Field.Retry,
            Field.Catch
        ]


class Chain(object):
    """
    Chain is a logical group of states, that resembles a linked list. The start state is the head of the *Chain* and the end state is the tail of the *Chain*.
    """

    def __init__(self, steps=[]):
        """
        Args:
            steps (list(State), optional): List of states to be chained in-order. (default: [])
        """
        if not isinstance(steps, list):
            raise TypeError("Chain takes a 'list' of steps. You provided an input that is not a list.")
        self.steps = []

        steps_expanded = []
        [steps_expanded.extend(step) if isinstance(step, Chain) else steps_expanded.append(step) for step in steps]
        for step in steps_expanded:
            if steps_expanded.count(step) > 1:
                raise DuplicateStatesInChain("Duplicate states in the chain.")
        list(map(self.append, steps_expanded))

    def __iter__(self):
        return iter(self.steps)

    @property
    def state_id(self):
        if len(self.steps) == 0:
            raise ValueError('The chain is empty')
        return self.steps[0].state_id

    def append(self, step):
        """Add a state at the tail end of the chain.

        Args:
            step (State): State to insert at the tail end of the chain.
        """
        if len(self.steps) == 0:
            self.steps.append(step)
        else:
            if step in self.steps:
                raise DuplicateStatesInChain("State '{step_name}' is already inside this chain. A chain cannot have duplicate states.".format(step_name=step.state_id))
            last_step = self.steps[-1]
            last_step.next(step)
            self.steps.append(step)

    def accept(self, visitor):
        for step in self.steps:
            step.accept(visitor)

    def __repr__(self):
        return '{}(steps={!r})'.format(
           self.__class__.__name__,
           self.steps
        )


class GraphVisitor(object):

    def __init__(self):
        self.states = {}

    def is_visited(self, state):
        return state.state_id in self.states

    def visit(self, state):
        self.states[state.state_id] = state.to_dict()


class ValidationVisitor(object):

    def __init__(self):
        self.states = {}

    def is_visited(self, state):
        if self.states.get(state.state_id) == state.to_dict():
            return True
        else:
            return False

    def visit(self, state):
        if state.state_id in self.states:
            raise ValueError("Each state in a workflow must have a unique state id. Found duplicate state id '{}' in workflow.".format(state.state_id))
        self.states[state.state_id] = state.to_dict()
        if state.next_step is None:
            return
        if not hasattr(state.next_step, 'fields') or Field.Parameters.value not in state.next_step.fields:
            return
        params = state.next_step.fields[Field.Parameters.value]
        valid, invalid_param_name = self._validate_next_step_params(params, state.step_output)
        if not valid:
            raise ValueError('State \'{state_name}\' is using an illegal placeholder for the \'{param_name}\' parameter.'.format(state_name=state.next_step.state_id, param_name=invalid_param_name))

    def _validate_next_step_params(self, params, step_output):
        for k, v in params.items():
            if isinstance(v, StepInput):
                if v is not step_output and not step_output.contains(v):
                    return False, k
            elif isinstance(v, dict):
                valid, invalid_param_name = self._validate_next_step_params(v, step_output)
                if not valid:
                    return valid, invalid_param_name
        return True, None

class Graph(Block):

    def __init__(self, branch, **kwargs):
        if not isinstance(branch, (State, Chain)):
            raise ValueError('Expected branch to be a State or a Chain, but got `{branch}`'.format(branch=branch))

        super(Graph, self).__init__(**kwargs)

        self.branch = branch
        self.states = {}
        self.build_graph(branch)

    def allowed_fields(self):
        return [
            Field.TimeoutSeconds,
            Field.Comment,
            Field.Version
        ]

    def contains(self, state):
        return self.states.get(state.state_id, False)

    def build_graph(self, state):
        graph_visitor = GraphVisitor()
        validation_visitor = ValidationVisitor()
        state.accept(validation_visitor)
        state.accept(graph_visitor)
        self.states = graph_visitor.states

    def to_dict(self):
        result = super(Graph, self).to_dict()
        result['StartAt'] = self.branch.state_id
        result['States'] = self.states
        return result


class FrozenGraph(Graph):

    def __init__(self, definition):
        if not isinstance(definition, dict):
            raise ValueError("Expected definition to be a dict, but got `{type}`.".format(type=type(definition)))
        self.definition = definition

    def to_dict(self):
        return self.definition

    @classmethod
    def from_json(cls, json_definition):
        return FrozenGraph(definition=json.loads(json_definition))
