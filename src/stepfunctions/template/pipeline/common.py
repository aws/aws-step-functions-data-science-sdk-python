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

from enum import Enum
from datetime import datetime

from stepfunctions.steps import Task
from stepfunctions.template.utils import replace_parameters_with_context_object


class StepId(Enum):

    Train             = 'Training'
    CreateModel       = 'Create Model'
    ConfigureEndpoint = 'Configure Endpoint'
    Deploy            = 'Deploy'

    TrainPreprocessor       = 'Train Preprocessor'
    CreatePreprocessorModel = 'Create Preprocessor Model'
    TransformInput          = 'Transform Input'
    CreatePipelineModel     = 'Create Pipeline Model'


class WorkflowTemplate(object):

    def __init__(self, s3_bucket, workflow, role, client, **kwargs):
        self.workflow = workflow
        self.role = role
        self.s3_bucket = s3_bucket
    
    def render_graph(self, portrait=False):
        return self.workflow.render_graph(portrait=portrait)

    def get_workflow(self):
        return self.workflow
    
    def _generate_timestamp(self):
        return datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    
    def _extract_input_template(self, definition):
        input_template = {}

        for step in definition.steps:
            if isinstance(step, Task):
                input_template[step.state_id] = step.parameters.copy()
                step.update_parameters(replace_parameters_with_context_object(step))
        
        return input_template
    
    def build_workflow_definition(self):
        raise NotImplementedError()

    def create(self):
        return self.workflow.create()
    
    def execute(self, **kwargs):
        raise NotImplementedError()

    def __repr__(self):
        return '{}(s3_bucket={!r}, workflow={!r}, role={!r})'.format(
            self.__class__.__name__,
            self.s3_bucket, self.workflow, self.role
        )
