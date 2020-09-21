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

import boto3
import json
import time
import logging

from enum import Enum
from datetime import datetime, date
from stepfunctions.exceptions import WorkflowNotFound, MissingRequiredParameter
from stepfunctions.steps import Graph, FrozenGraph
from stepfunctions.workflow.widgets import WorkflowGraphWidget, ExecutionGraphWidget, EventsTableWidget, ExecutionsTableWidget, WorkflowsTableWidget
from stepfunctions.workflow.utils import append_user_agent_to_client
from stepfunctions.workflow.widgets.utils import create_sfn_workflow_url, create_sfn_execution_url, get_timestamp
from stepfunctions.workflow.cloudformation import build_cloudformation_template


logger = logging.getLogger('stepfunctions')

try:
    from IPython.core.display import HTML
except ImportError as e:
    logger.warning("IPython failed to import. Visualization features will be impaired or broken.")


def json_serializer(obj):
    if isinstance(obj, (datetime, date)):
        return get_timestamp(obj)
    raise TypeError ("Type %s not serializable" % type(obj))


class EventsList(list):

    def to_html(self):
        return EventsTableWidget(self).show()


class WorkflowList(list):

    def to_html(self):
        return WorkflowsTableWidget(self).show()


class ExecutionsList(list):

    def to_html(self):
        return ExecutionsTableWidget(self).show()


class ExecutionStatus(Enum):

    """
    Enumeration for workflow status.
    """

    Running   = 'RUNNING'   #:
    Succeeded = 'SUCCEEDED' #:
    Failed    = 'FAILED'    #:
    TimedOut  = 'TIMED_OUT' #:
    Aborted   = 'ABORTED'   #:


class Workflow(object):

    """
    Class for creating and managing a workflow.
    """

    @classmethod
    def list_workflows(cls, max_items=100, client=None, html=False):
        """
        Lists all the workflows in the account.

        Args:
            max_items (int, optional): The maximum number of items to be returned. (default: 100)
            client (SFN.Client, optional): boto3 client to use for the query. If not provided, a default boto3 client for Step Functions will be automatically created and used. (default: None)
            html (bool, optional): Renders the list as an HTML table (If running in an IPython environment). If the parameter is not provided, or set to False, a Python list is returned. (default: False)

        Returns:
            list: The list of workflows. Refer to :meth:`.SFN.Client.list_state_machines()` for the response structure.
        """
        if client is None:
            logger.debug("The argument 'client' is not provided. Creating a new boto3 client instance with default settings.")
            client = boto3.client('stepfunctions')

        logger.debug("Retrieving list of workflows from AWS Step Functions.")
        paginator = client.get_paginator('list_state_machines')
        params = {
            'PaginationConfig': {
                'MaxItems': max_items,
                'PageSize': 1000
            }
        }
        response_iterator = paginator.paginate(**params)

        workflows = []
        for page in response_iterator:
            for workflow in page['stateMachines']:
                workflows.append(workflow)
        workflows_list = WorkflowList(workflows)

        if html:
            return HTML(workflows_list.to_html())
        else:
            return workflows_list

    @classmethod
    def attach(cls, state_machine_arn, client=None):
        """
        Factory method to create an instance attached to an exisiting workflow in Step Functions.

        Arguments:
            state_machine_arn (str): The Amazon Resource Name (ARN) of the existing workflow.
            client (SFN.Client, optional): boto3 client to use for attaching the existing workflow in Step Functions to the Workflow object.
                                           If not provided, a default boto3 client for Step Functions will be automatically created and used. (default: None)

        Returns:
            Workflow: Workflow object attached to the existing workflow in Step Functions.
        """
        if client is None:
            logger.debug("The argument 'client' is not provided. Creating a new boto3 client instance with default settings.")
            client = boto3.client('stepfunctions')

        response = client.describe_state_machine(stateMachineArn=state_machine_arn)
        return Workflow(
            name=response['name'],
            definition=FrozenGraph.from_json(response['definition']),
            role=response['roleArn'],
            state_machine_arn=response['stateMachineArn'],
            client=client
        )

    def __init__(self, name, definition, role, tags=[], execution_input=None, timeout_seconds=None, comment=None, version=None, state_machine_arn=None, format_json=True, client=None):
        """
        Args:
            name (str): The name of the workflow. A name must not contain:

                * whitespace
                * brackets < > { } [ ]
                * wildcard characters ? *
                * special characters " # % \\ ^ | ~ ` $ & , ; : /
                * control characters (U+0000-001F , U+007F-009F )
            definition (State or Chain): The `Amazon States Language <https://states-language.net/spec.html>`_ definition of the workflow.
            role (str): The Amazon Resource Name (ARN) of the IAM role to use for creating, managing, and running the workflow.
            tags (list): Tags to be added when creating a workflow. Tags are key-value pairs that can be associated with Step Functions workflows and activities. (default: [])
            execution_input (ExecutionInput, optional): Placeholder collection that defines the placeholder variables for the workflow execution. \
                                                        This is also used to validate inputs provided when executing the workflow. (default: None)
            timeout_seconds (int, optional): The maximum number of seconds an execution of the workflow can run. If it runs longer than the specified time, the workflow run fails with a `States.Timeout` Error Name. (default: None)
            comment (str, optional): A human-readable description of the workflow. (default: None)
            version (str, optional): The version of the Amazon States Language used in the workflow. (default: None)
            state_machine_arn (str, optional): The Amazon Resource Name (ARN) of the workflow. (default: None)
            format_json (bool, optional): Boolean flag set to `True` if workflow definition and execution inputs should be prettified for this workflow. `False`, otherwise. (default: True)
            client (SFN.Client, optional): boto3 client to use for creating, managing, and running the workflow on Step Functions. If not provided, a default boto3 client for Step Functions will be automatically created and used. (default: None)
        """
        self.timeout_seconds = timeout_seconds
        self.comment = comment
        self.version = version
        if isinstance(definition, Graph):
            self.definition = definition
        else:
            self.definition = Graph(
                definition,
                timeout_seconds=self.timeout_seconds,
                comment=self.comment,
                version=self.version
            )
        self.name = name
        self.role = role
        self.tags = tags
        self.workflow_input = execution_input

        if client:
            self.client = client
        else:
            self.client = boto3.client('stepfunctions')
        append_user_agent_to_client(self.client)

        self.format_json = format_json
        self.state_machine_arn = state_machine_arn

    def create(self):
        """
        Creates the workflow on Step Functions.

        Returns:
            str: The Amazon Resource Name (ARN) of the workflow created. If the workflow already existed, the ARN of the existing workflow is returned.
        """
        if self.state_machine_arn is not None:
            logger.warning("The workflow already exists on AWS Step Functions. No action will be performed.")
            return self.state_machine_arn

        try:
            self.state_machine_arn = self._create()
        except self.client.exceptions.StateMachineAlreadyExists as e:
            self.state_machine_arn = self._extract_state_machine_arn(e)
            logger.error("A workflow with the same name already exists on AWS Step Functions. To update a workflow, use Workflow.update().")

        return self.state_machine_arn

    def _create(self):
        response = self.client.create_state_machine(
            name=self.name,
            definition=self.definition.to_json(pretty=self.format_json),
            roleArn=self.role,
            tags=self.tags
        )
        logger.info("Workflow created successfully on AWS Step Functions.")
        return response['stateMachineArn']

    def update(self, definition=None, role=None):
        """
        Updates an existing state machine by modifying its definition and/or role. Executions started immediately after calling this method may use the previous definition and role.

        Args:
            definition (State or Chain, optional): The `Amazon States Language <https://states-language.net/spec.html>`_ definition to update the workflow with. (default: None)
            role (str, optional): The Amazon Resource Name (ARN) of the IAM role to use for creating, managing, and running the workflow. (default: None)

        Returns:
            str: The state machine definition and/or role updated. If the update fails, None will be returned.
        """

        if definition is None and role is None:
            raise MissingRequiredParameter("A new definition and/or role must be provided to update an existing workflow.")

        if self.state_machine_arn is None:
            raise WorkflowNotFound("Local workflow instance does not point to an existing workflow on AWS StepFunctions. Please consider using Workflow.create(...) to create a new workflow, or Workflow.attach(...) to attach the instance to an existing workflow on AWS Step Functions.")

        if definition:
            if isinstance(definition, Graph):
                self.definition = definition
            else:
                self.definition = Graph(
                    definition,
                    timeout_seconds=self.timeout_seconds,
                    comment=self.comment,
                    version=self.version
                )

        if role:
            self.role = role

        response = self.client.update_state_machine(
            stateMachineArn=self.state_machine_arn,
            definition=self.definition.to_json(pretty=self.format_json),
            roleArn=self.role
        )
        logger.info("Workflow updated successfully on AWS Step Functions. All execute() calls will use the updated definition and role within a few seconds. ")
        return self.state_machine_arn

    def _extract_state_machine_arn(self, exception):
        """
        Message Example: {
            'Error': {
                'Message': "State Machine Already Exists: 'arn:aws:states:us-east-1:1234567890:stateMachine:test'"
            }
        }
        """
        message = exception.response['Error']['Message']
        return message.split("'")[1]

    def execute(self, name=None, inputs=None):
        """
        Starts a single execution of the workflow.

        Args:
            name (str, optional): The name of the workflow execution. If one is not provided, a workflow execution name will be auto-generated. (default: None)
            inputs (str, list or dict, optional): Input data for the workflow execution. (default: None)

        Returns:
            stepfunctions.workflow.Execution: An execution instance of the workflow.
        """
        if self.workflow_input:
            validation_result = self.workflow_input.validate(inputs)
            if validation_result.valid is False:
                raise ValueError("Expected run input with the schema: {}".format(self.workflow_input.get_schema_as_json()))

        if self.state_machine_arn is None:
            raise WorkflowNotFound("Local workflow instance does not point to an existing workflow on AWS StepFunctions. Before executing a workflow, call Workflow.create(...) or Workflow.attach(...).")

        params = {
            'stateMachineArn': self.state_machine_arn
        }
        if name is not None:
            params['name'] = name

        if inputs is not None:
            if self.format_json:
                params['input'] = json.dumps(inputs, indent=4)
            else:
                params['input'] = json.dumps(inputs)

        response = self.client.start_execution(**params)
        logger.info("Workflow execution started successfully on AWS Step Functions.")

        # name is None because boto3 client.start_execution only returns startDate and executionArn
        return Execution(
            workflow=self,
            execution_arn=response['executionArn'],
            start_date=response['startDate'],
            status=ExecutionStatus.Running,
            client=self.client
        )

    def list_executions(self, max_items=100, status_filter=None, html=False):
        """
        Lists the executions for the workflow.

        Args:
            max_items (int, optional): The maximum number of items to be returned. (default: 100)
            status_filter (ExecutionStatus, optional): If specified, only list the executions whose current status matches the given filter. (default: None)
            html (bool, optional): Renders the list as an HTML table (If running in an IPython environment). If the parameter is not provided, or set to False, a Python list is returned. (default: False)

        Returns:
            list(stepfunctions.workflow.Execution): List of workflow run instances.
        """
        if self.state_machine_arn is None:
            return ExecutionsList()

        logger.debug("Retrieving list of executions from AWS Step Functions.")
        paginator = self.client.get_paginator('list_executions')
        params = {
            'stateMachineArn': self.state_machine_arn,
            'PaginationConfig': {
                'MaxItems': max_items,
                'PageSize': 1000
            }
        }
        if status_filter is not None:
            params['statusFilter'] = status_filter.value
        response_iterator = paginator.paginate(**params)

        runs = [
            Execution(
                name=execution['name'],
                workflow=self,
                execution_arn=execution['executionArn'],
                start_date=execution['startDate'],
                stop_date=execution.get('stopDate', None),
                status=execution['status'],
                client=self.client
        ) for page in response_iterator for execution in page['executions']]
        executions_list = ExecutionsList(runs)

        if html:
            return HTML(executions_list.to_html())
        else:
            return executions_list

    def delete(self):
        """
        Deletes the workflow, if it exists.
        """
        if self.state_machine_arn is not None:
            self.client.delete_state_machine(stateMachineArn=self.state_machine_arn)
            logger.info("Workflow has been marked for deletion. If the workflow has running executions, it will be deleted when all executions are stopped.")

    def render_graph(self, portrait=False):
        """
        Renders a visualization of the workflow graph.

        Args:
            portrait (bool, optional): Boolean flag set to `True` if the workflow graph should be rendered in portrait orientation. Set to `False`, if the graph should be rendered in landscape orientation. (default: False)
        """
        widget = WorkflowGraphWidget(self.definition.to_json())
        return widget.show(portrait=portrait)

    def get_cloudformation_template(self):
        """
        Returns a CloudFormation template that contains only the StateMachine resource. To reuse the CloudFormation template in a different region, please make sure to update the region specific AWS resources (e.g: Lambda ARN, Training Image) in the StateMachine definition.
        """
        return build_cloudformation_template(self)

    def __repr__(self):
        return '{}(name={!r}, role={!r}, state_machine_arn={!r})'.format(
           self.__class__.__name__,
           self.name, self.role, self.state_machine_arn
        )

    def _repr_html_(self):
        if self.state_machine_arn:
            return 'Workflow: <a target="_blank" href="{}">{}</a>'.format(create_sfn_workflow_url(self.state_machine_arn), self.state_machine_arn)
        else:
            return 'Workflow: Does Not Exist.'


class Execution(object):

    """
    Class for managing a workflow execution.
    """

    def __init__(self, workflow, execution_arn, start_date, status, client=None, name=None, stop_date=None):
        """
        Args:
            workflow (Workflow): Step Functions workflow instance.
            execution_arn (str): The Amazon Resource Name (ARN) of the workflow execution.
            start_date (datetime.datetime): The date the workflow execution was started.
            status (RunStatus): Status of the workflow execution.
            client (SFN.Client, optional): boto3 client to use for running and managing the workflow executions on Step Functions. If no client is provided, the boto3 client from the parent workflow will be used. (default: None)
            name (str, optional): Name for the workflow execution. (default: None)
            stop_date (datetime.datetime, optional): The date the workflow execution was stopped, if applicable. (default: None)
        """
        self.name = name
        self.workflow = workflow
        self.execution_arn = execution_arn
        self.start_date = start_date
        self.stop_date = stop_date
        self.status = status
        if client:
            self.client = client
            append_user_agent_to_client(self.client)
        else:
            self.client = self.workflow.client

    def stop(self, cause=None, error=None):
        """
        Stops a workflow execution.

        Args:
            error (str, optional): The error code of the failure. (default: None)
            cause (str, optional): A more detailed explanation of the cause of the failure. (default: None)

        Returns:
            dict: Datetime of when the workflow execution was stopped. Example below::

                {
                    'stopDate': datetime(2015, 1, 1)
                }

            **Response structure**:

            * (dict)
                * stopDate (datetime): The date the workflow execution is stopped
        """
        params = {
            'executionArn': self.execution_arn
        }
        if cause is not None:
            params['cause'] = cause
        if error is not None:
            params['error'] = error
        response = self.client.stop_execution(**params)
        logger.info("Stopping the execution %s of the workflow %s on AWS Step Functions.", self.execution_arn, self.workflow.name)
        return response

    def list_events(self, max_items=100, reverse_order=False, html=False):
        """
        Lists the events in the workflow execution.

        Args:
            max_items (int, optional): The maximum number of items to be returned. (default: 100)
            reverse_order (bool, optional): Boolean flag set to `True` if the events should be listed in reverse chronological order. Set to `False`, if the order should be in chronological order. (default: False)
            html (bool, optional): Renders the list as an HTML table (If running in an IPython environment). If the parameter is not provided, or set to False, a Python list is returned. (default: False)

        Returns:
            dict: Object containing the list of workflow execution events. Refer to :meth:`.SFN.Client.get_execution_history()` for the response structure.
        """
        logger.debug("Retrieving list of history events for your execution from AWS Step Functions.")
        paginator = self.client.get_paginator('get_execution_history')
        params = {
            'executionArn': self.execution_arn,
            'reverseOrder': reverse_order,
            'PaginationConfig': {
                'MaxItems': max_items,
                'PageSize': 1000
            }
        }
        response_iterator = paginator.paginate(**params)

        events = []
        for page in response_iterator:
            for event in page['events']:
                events.append(event)
        events_list = EventsList(events)

        if html:
            return HTML(events_list.to_html())
        else:
            return events_list

    def describe(self):
        """
        Describes a workflow execution.

        Returns:
            dict: Details of the workflow execution.

            **Response structure**:

            * (dict)

                * executionArn (string): The Amazon Resource Name (ARN) that identifies the workflow execution.
                * stateMachineArn (string): The Amazon Resource Name (ARN) of the workflow that was executed.
                * name (string): The name of the workflow execution.
                * status (string): The current status of the workflow execution.
                * startDate (datetime): The date the workflow execution is started.
                * stopDate (datetime): If the workflow execution has already ended, the date the execution stopped.
                * input (string): The string that contains the JSON input data of the workflow execution.
                * output (string): The JSON output data of the workflow execution.
        """
        return self.client.describe_execution(executionArn=self.execution_arn)

    def render_progress(self, portrait=False, max_events=25000):
        """
        Renders a visualization of the workflow execution graph.

        Args:
            portrait (bool, optional): Boolean flag set to `True` if the workflow execution graph should be rendered in portrait orientation. Set to `False`, if the graph should be rendered in landscape orientation. (default: False)
            max_events (int, optional): Specifies the number of events to be visualized in the workflow execution graph. (default: 25000)
        """
        events = self.list_events(max_items=max_events)
        widget = ExecutionGraphWidget(
            self.workflow.definition.to_json(),
            json.dumps(events, default=json_serializer),
            execution_arn=self.execution_arn)
        return widget.show(portrait=portrait)

    def get_input(self):
        """
        Get the input for the workflow execution.

        Returns:
            list or dict: Workflow execution input.
        """
        run_input = self.describe().get('input', None)
        if run_input is None:
            return run_input
        return json.loads(run_input)

    def get_output(self, wait=False):
        """
        Get the output for the workflow execution.

        Args:
            wait (bool, optional): Boolean flag set to `True` if the call should wait for a running workflow execution to end before returning the output. Set to `False`, otherwise. Note that if the status is running, and `wait` is set to `True`, this will be a blocking call. (default: False)

        Returns:
            list or dict: Workflow execution output.
        """
        while wait and self.describe()['status'] == 'RUNNING':
            time.sleep(1)
        output = self.describe().get('output', None)
        if output is None:
            return output
        return json.loads(output)

    def __repr__(self):
        return '{}(execution_arn={!r}, name={!r}, status={!r}, start_date={!r})'.format(
           self.__class__.__name__,
           self.execution_arn, self.name, self.status, self.start_date
        )

    def _repr_html_(self):
        return 'Execution: <a target="_blank" href="{}">{}</a>'.format(create_sfn_execution_url(self.execution_arn), self.execution_arn)
