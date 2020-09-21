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

import random
import json
import logging

logger = logging.getLogger('stepfunctions')

try:
    from IPython.core.display import HTML
    __IPYTHON_IMPORTED__ = True
except ImportError as e:
    logger.warning("IPython failed to import. Visualization features will be impaired or broken.")
    __IPYTHON_IMPORTED__ = False

from string import Template

from stepfunctions.workflow.widgets.utils import create_sfn_execution_url

JSLIB_URL = 'https://do0of8uwbahzz.cloudfront.net/sfn'
CSS_URL = 'https://do0of8uwbahzz.cloudfront.net/graph.css'

HTML_TEMPLATE = """
<link rel="stylesheet" type="text/css" href="$css">
<div id="$element_id" class="workflowgraph">
    $graph_legend_template
    <svg></svg>
    {console_snippet}
</div>

<script type="text/javascript">
{code_snippet}
</script>
"""

EXECUTION_URL_TEMPLATE = """<a href="$console" target="_blank"> Inspect in AWS Step Functions </a>"""

WORKFLOW_GRAPH_SCRIPT_TEMPLATE = """
require.config({
    paths: {
        sfn: "$jslib",
    }
});

require(['sfn'], function(sfn) {
    var element = document.getElementById('$element_id')

    var options = {
        width: parseFloat(getComputedStyle(element, null).width.replace("px", "")),
        height: 600,
        layout: '$layout',
        resizeHeight: true
    };

    var definition = $definition;
    var elementId = '#$element_id';

    var graph = new sfn.StateMachineGraph(definition, elementId, options);
    graph.render();
});
"""

EXECUTION_GRAPH_SCRIPT_TEMPLATE = """
require.config({
    paths: {
        sfn: "$jslib",
    }
});

require(['sfn'], function(sfn) {
    var element = document.getElementById('$element_id')

    var options = {
        width: parseFloat(getComputedStyle(element, null).width.replace("px", "")),
        height: 1000,
        layout: '$layout',
        resizeHeight: true
    };

    var definition = $definition;
    var elementId = '#$element_id';
    var events = { 'events': $events };

    var graph = new sfn.StateMachineExecutionGraph(definition, events, elementId, options);
    graph.render();
});
"""

EXECUTION_GRAPH_LEGEND_TEMPLATE = """
    <style>
        .graph-legend ul {
            list-style-type: none;
            padding: 10px;
            padding-left: 0;
            margin: 0;
            position: absolute;
            top: 0;
            background: transparent;
        }

        .graph-legend li {
            margin-left: 10px;
            display: inline-block;
        }

        .graph-legend li > div {
            width: 10px;
            height: 10px;
            display: inline-block;
        }

        .graph-legend .success { background-color: #2BD62E }
        .graph-legend .failed { background-color: #DE322F }
        .graph-legend .cancelled { background-color: #DDDDDD }
        .graph-legend .in-progress { background-color: #53C9ED }
        .graph-legend .caught-error { background-color: #FFA500 }
    </style>
    <div class="graph-legend">
        <ul>
            <li>
                <div class="success"></div>
                <span>Success</span>
            </li>
            <li>
                <div class="failed"></div>
                <span>Failed</span>
            </li>
            <li>
                <div class="cancelled"></div>
                <span>Cancelled</span>
            </li>
            <li>
                <div class="in-progress"></div>
                <span>In Progress</span>
            </li>
            <li>
                <div class="caught-error"></div>
                <span>Caught Error</span>
            </li>
        </ul>
    </div>
"""

class WorkflowGraphWidget(object):

    def __init__(self, json_definition):
        self.json_definition = json_definition
        self.element_id = 'graph-%d' % random.randint(0, 999)
        self.layout = 'TB'
        self.template = Template(HTML_TEMPLATE.format(
            code_snippet=WORKFLOW_GRAPH_SCRIPT_TEMPLATE,
            console_snippet=''))

    def show(self, portrait=True):
        if __IPYTHON_IMPORTED__ is False:
            logger.error("IPython failed to import. Widgets/graphs cannot be visualized.")
            return ""
        if portrait is False:
            self.layout = 'LR'
        else:
            self.layout = 'TB'

        return HTML(self.template.substitute({
            'element_id': self.element_id,
            'definition': self.json_definition,
            'layout': self.layout,
            'css': CSS_URL,
            'jslib': JSLIB_URL,
            'graph_legend_template': ""
        }))

class ExecutionGraphWidget(object):

    def __init__(self, json_definition, json_events, execution_arn):
        self.json_definition = json_definition
        self.json_events = json_events
        self.element_id = 'graph-%d' % random.randint(0, 999)
        self.layout = 'TB'
        self.template = Template(HTML_TEMPLATE.format(
            code_snippet=EXECUTION_GRAPH_SCRIPT_TEMPLATE,
            console_snippet=EXECUTION_URL_TEMPLATE))
        self.console_url = create_sfn_execution_url(execution_arn)

    def show(self, portrait=True):
        if __IPYTHON_IMPORTED__ is False:
            logger.error("IPython failed to import. Widgets/graphs cannot be visualized.")
            return ""
        if portrait is False:
            self.layout = 'LR'
        else:
            self.layout = 'TB'

        return HTML(self.template.substitute({
            'element_id': self.element_id,
            'definition': self.json_definition,
            'events': self.json_events,
            'layout': self.layout,
            'css': CSS_URL,
            'jslib': JSLIB_URL,
            'graph_legend_template': EXECUTION_GRAPH_LEGEND_TEMPLATE,
            'console': self.console_url
        }))
