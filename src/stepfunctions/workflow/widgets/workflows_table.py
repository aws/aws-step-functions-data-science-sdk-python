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

from datetime import datetime
from string import Template

from stepfunctions.workflow.widgets.utils import format_time, create_sfn_workflow_url, AWS_TABLE_CSS

TABLE_TEMPLATE = """
    <style>
        $aws_table_css
        $custom_css
    </style>
    <table class="table-widget">
        <thead>
            <tr>
                <th>Name</th>
                <th>Creation Date</th>
            </tr>
        </thead>
        <tbody>
            {table_rows}
        </tbody>
    </table>
"""

TABLE_ROW_TEMPLATE = """
    <tr class="awsui-table-row">
        <td>
            <a href="$state_machine_url" target="_blank" class="awsui">$name</a>
        </td>
        <td>$creation_date</td>
    </tr>
"""

CSS_TEMPLATE = """
    * {
        box-sizing: border-box;
    }

    .table-widget {
        min-width: 100%;
        font-size: 14px;
        line-height: 28px;
        color: #545b64;
        border-spacing: 0;
        background-color: #fff;
        border-color: grey;
        background: #fafafa;
    }

    .table-widget thead th {
        text-align: left !important;
        color: #879596;
        padding: 0.3em 2em;
        border-bottom: 1px solid #eaeded;
        min-height: 4rem;
        line-height: 28px;
    }

    .table-widget td {
        /* padding: 24px 18px; */
        padding: 0.4em 2em;
        line-height: 28px;
        text-align: left !important;
        background: #fff;
        border-bottom: 1px solid #eaeded;
        border-top: 1px solid transparent;
    }

    .table-widget td:before {
        content: "";
        height: 3rem;
    }

    .table-widget .clickable-cell {
        cursor: pointer;
    }

    .hide {
        display: none;
    }

    .triangle-right {
        width: 0;
        height: 0;
        border-top: 5px solid transparent;
        border-left: 8px solid #545b64;
        border-bottom: 5px solid transparent;
        margin-right: 5px;
    }

    a.awsui {
        text-decoration: none !important;
        color: #007dbc;
    }

    a.awsui:hover {
        text-decoration: underline !important;
    }
"""

class WorkflowsTableWidget(object):

    def __init__(self, workflows):
        table_rows = [Template(TABLE_ROW_TEMPLATE).substitute(
            state_machine_url=create_sfn_workflow_url(workflow['stateMachineArn']),
            name=workflow['name'],
            creation_date=format_time(workflow['creationDate']),
        ) for workflow in workflows]
        
        self.template = Template(TABLE_TEMPLATE.format(table_rows='\n'.join(table_rows)))

    def show(self):
        return self.template.substitute({
            'aws_table_css': AWS_TABLE_CSS,
            'custom_css': CSS_TEMPLATE
        })
