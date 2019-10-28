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
from ast import literal_eval
from string import Template

from stepfunctions.workflow.widgets.utils import (
    format_time, 
    get_elapsed_ms, 
    AWS_TABLE_CSS,
    sagemaker_console_link
)

LAMBDA_SERVICE_NAME = "lambda"
LAMBDA_FUNCTION_RESOURCE_TYPE = "function"
LAMBDA_ARN_SEGMENT_LENGTH = 7
SAGEMAKER_JOB_NAME_MAP = {
    'createTrainingJob': 'Sagemaker training job',
    'createTrainingJob.sync': 'Sagemaker training job',
    'createTransformJob': 'Sagemaker transform job',
    'createTransformJob.sync': 'Sagemaker transform job',
    'createModel': 'Sagemaker model',
    'createModel.sync': 'Sagemaker model',
    'createEndpointConfig': 'Sagemaker endpoint configuration',
    'createEndpointConfig.sync': 'Sagemaker endpoint configuration',
    'createEndpoint': 'Sagemaker endpoint',
    'createEndpoint.sync': 'Sagemaker endpoint'
}

TABLE_TEMPLATE = """
    <style>
        $aws_table_css
        $custom_css
    </style>
    <table class="table-widget">
        <thead>
            <tr>
                <th style="width: 60px">ID</th>
                <th>Type</th>
                <th>Step</th>
                <th>Resource</th>
                <th>Elapsed Time (ms)</th>
                <th>Timestamp</th>
            </tr>
        </thead>
        <tbody>
            {table_rows}
        </tbody>
    </table>
    <script type="text/javascript">
        $js
    </script>
"""

TABLE_ROW_TEMPLATE = """
    <tr class="awsui-table-row">
        <td class="awsui-util-pl-xs clickable-cell">
            <div class="toggle-icon"></div>
            <span>$event_id</span>
        </td>
        <td>$event_type</td>
        <td>$step</td>
        <td><a $resource_url target="_blank">$resource</a></td>
        <td>$elapsed_time</td>
        <td>$timestamp</td>
    </tr>
    <tr class="hide">
        <td class="execution-event-detail" colspan="6">
            <pre>$event_detail</pre>
        </td>
    </tr>
"""

JS_TEMPLATE = """
    var clickableCells = document.getElementsByClassName("clickable-cell");
    for (var cell of clickableCells) {
        cell.addEventListener("click", function(e) {
            var currentRow = e.srcElement.closest("tr");
            var toggleRow = currentRow.nextElementSibling;
            var toggleArrow = currentRow.getElementsByClassName("toggle-icon")[0];

            toggleRow.classList.toggle("hide");
            toggleArrow.classList.toggle("open");
        });
    }
"""

CSS_TEMPLATE = """
    .table-widget .clickable-cell {
        padding-left: 0.1em;
        cursor: pointer;
    }

    .toggle-icon {
        display: inline-block;
        width: 0;
        height: 0;
        border-top: 5px solid transparent;
        border-left: 8px solid #545b64;
        border-bottom: 5px solid transparent;
        margin-right: 5px;
    }

    .toggle-icon.open {
        -webkit-transform: rotate(90deg);
        -ms-transform: rotate(90deg);
        transform: rotate(90deg);
    }
"""
    
class EventsTableWidget(object):
    
    def __init__(self, events):
        self.eventIdToLambdaArnMap = {}
        self.previous_step_name = ""
        self.previous_job_name = ""
        start_datetime = None

        if len(events) > 0:
            start_datetime = events[0].get("timestamp")
        
        table_rows = [Template(TABLE_ROW_TEMPLATE).substitute(
            event_id=str(event.get("id")), 
            event_type=event.get("type"),
            step=self._get_step(event),
            resource=self._get_resource(event, True),
            resource_url=self._get_resource_url(event),
            elapsed_time=get_elapsed_ms(start_datetime, event.get("timestamp")),
            timestamp=format_time(event.get("timestamp")),
            event_detail=self._format_event_detail(event)
        ) for event in events]

        self.template = Template(TABLE_TEMPLATE.format(table_rows='\n'.join(table_rows)))
    
    def show(self):
        return self.template.safe_substitute({
            'aws_table_css': AWS_TABLE_CSS,
            'custom_css': CSS_TEMPLATE,
            'js': JS_TEMPLATE
        })
    
    def _get_step_detail(self, event):
        switcher = {
            "ChoiceStateEntered": event.get("stateEnteredEventDetails", {}),
            "ChoiceStateExited": event.get("stateExitedEventDetails", {}),
            "FailStateEntered": event.get("stateEnteredEventDetails", {}),
            "MapStateEntered": event.get("stateEnteredEventDetails", {}),
            "MapStateExited": event.get("stateExitedEventDetails", {}),
            "ParallelStateEntered": event.get("stateEnteredEventDetails", {}),
            "ParallelStateExited": event.get("stateExitedEventDetails", {}),
            "PassStateEntered": event.get("stateEnteredEventDetails", {}),
            "PassStateExited": event.get("stateExitedEventDetails", {}),
            "SucceedStateEntered": event.get("stateEnteredEventDetails", {}),
            "SucceedStateExited": event.get("stateExitedEventDetails", {}),
            "TaskStateEntered": event.get("stateEnteredEventDetails", {}),
            "TaskStateExited": event.get("stateExitedEventDetails", {}),
            "WaitStateEntered": event.get("stateEnteredEventDetails", {}),
            "WaitStateExited": event.get("stateExitedEventDetails", {}),
            "MapIterationAborted": event.get("mapIterationAbortedEventDetails", {}),
            "MapIterationFailed": event.get("mapIterationFailedEventDetails", {}),
            "MapIterationStarted": event.get("mapIterationStartedEventDetails", {}),
            "MapIterationSucceeded": event.get("mapIterationSucceededEventDetails", {}),
            "ExecutionFailed": event.get("executionFailedEventDetails", {}),
            "ExecutionStarted": event.get("executionStartedEventDetails", {}),
            "ExecutionSucceeded": event.get("executionSucceededEventDetails", {}),
            "ExecutionAborted": event.get("executionAbortedEventDetails", {}),
            "ExecutionTimedOut": event.get("executionTimedOutEventDetails", {}),
            "LambdaFunctionScheduled": event.get("lambdaFunctionScheduledEventDetails", {}),
            "LambdaFunctionScheduleFailed": event.get("lambdaFunctionScheduleFailedEventDetails", {}),
            "LambdaFunctionStartFailed": event.get("lambdaFunctionStartFailedEventDetails", {}),
            "LambdaFunctionSucceeded": event.get("lambdaFunctionSucceededEventDetails", {}),
            "LambdaFunctionFailed": event.get("lambdaFunctionFailedEventDetails", {}),
            "LambdaFunctionTimedOut": event.get("lambdaFunctionTimedOutEventDetails", {}),
            "TaskStarted": event.get("taskStartedEventDetails", {}),
            "TaskSubmitted": event.get("taskSubmittedEventDetails", {}),
            "TaskScheduled": event.get("taskScheduledEventDetails", {}),
            "TaskSucceeded": event.get("taskSucceededEventDetails", {}),
            "TaskFailed": event.get("taskFailedEventDetails", {})
        }

        return switcher.get(event.get("type"), {})
    
    # Tries to get step name, if it can not find, return the previous step's name
    def _get_step(self, event):
        if event.get("type") in (
            "ExecutionFailed",
            "ExecutionStarted",
            "ExecutionSucceeded",
            "ExecutionAborted",
            "ExecutionTimedOut"
        ):
            step_name = ""
            self.previous_step_name = ""
        else:
            step_name = self._get_step_detail(event).get("name")
            if not step_name:
                step_name = self.previous_step_name
            else:
                self.previous_step_name = step_name
                
        return step_name

    def _get_resource(self, event, mapped_value=False):
        # check that it is a lambda, sagemaker or just a regular execution
        if self._is_correct_lambda_arn_sequence(self._get_lambda_arn(event)):
            return "Lambda"

        # check if it has a resource
        elif self._has_resource(event):
            
            # check if it is a sagemaker resource
            step_details = self._get_step_detail(event)
            if step_details.get("resourceType") == "sagemaker":
                sagemaker_resource = step_details.get("resource")

                if mapped_value:
                    return SAGEMAKER_JOB_NAME_MAP[sagemaker_resource]

                return sagemaker_resource

            return "Step Functions execution"

        # if not a resource, return -
        return "-"

    def _get_resource_url(self, event):
        resource = self._get_resource(event)

        if "createTrainingJob" in resource:
            job_name = self._get_sagemaker_resource_job_name(event, "TrainingJobName")
            return 'href="{}"'.format(sagemaker_console_link('jobs', job_name))
        
        if "createTransformJob" in resource:
            job_name = self._get_sagemaker_resource_job_name(event, "TransformJobName")
            return 'href="{}"'.format(sagemaker_console_link('transformJobs', job_name))
        
        if "createModel" in resource:
            job_name = self._get_sagemaker_resource_job_name(event, "ModelName")
            return 'href="{}"'.format(sagemaker_console_link('models', job_name))

        if "createEndpointConfig" in resource:
            job_name = self._get_sagemaker_resource_job_name(event, "EndpointConfigName")
            return 'href="{}"'.format(sagemaker_console_link('endpointConfig', job_name))

        if "createEndpoint" in resource:
            job_name = self._get_sagemaker_resource_job_name(event, "EndpointName")
            return 'href="{}"'.format(sagemaker_console_link('endpoints', job_name))

        self.previous_job_name = ""
        return "class='disabled'"

    def _get_sagemaker_resource_job_name(self, event, job_name_key):
        step_details = self._get_step_detail(event)
        job_name = literal_eval(step_details.get("parameters", "{}")).get(job_name_key, "")
        if job_name == "":
            job_name = self.previous_job_name
        else: 
            self.previous_job_name = job_name
            
        return job_name

    def _has_resource(self, event):
        return event.get("type") in (
            "TaskSucceeded",
            "TaskSubmitted",
            "TaskScheduled",
            "TaskStarted"
        )

    def _get_lambda_arn(self, event):
        resource_arn = "-"
        event_type = event.get("type")

        if event_type == "LambdaFunctionScheduled":
            resource_arn = event.get("lambdaFunctionScheduledEventDetails").get("resource")
        elif event_type in {
            "LambdaFunctionScheduleFailed",
            "LambdaFunctionFailed",
            "LambdaFunctionStartFailed",
            "LambdaFunctionStarted",
            "LambdaFunctionSucceeded",
            "LambdaFunctionTimedOut"
        }:
            resource_arn = self.eventIdToLambdaArnMap[event.get("previousEventId")]

        self.eventIdToLambdaArnMap[event.get("id")] = resource_arn
        return resource_arn

    def _is_correct_lambda_arn_sequence(self, lambda_arn):
        lambda_arn_segments = lambda_arn.split(":")
        return (len(lambda_arn_segments) == LAMBDA_ARN_SEGMENT_LENGTH and 
                lambda_arn_segments[2] == LAMBDA_SERVICE_NAME and 
                lambda_arn_segments[5] == LAMBDA_FUNCTION_RESOURCE_TYPE)

    def _format_event_detail(self, event):
        event_details = self._get_step_detail(event)
        self._unpack_to_proper_dict(event_details)
        return json.dumps(event_details, indent=4)

    def _unpack_to_proper_dict(self, dictionary):
        for k, v in dictionary.items():
            if isinstance(v, dict):
                self._unpack_to_proper_dict(v)
            else: 
                dictionary[k] = self._load_json(v)

    def _load_json(self, value):
        try:
            return json.loads(value)
        except ValueError as e:
            return value