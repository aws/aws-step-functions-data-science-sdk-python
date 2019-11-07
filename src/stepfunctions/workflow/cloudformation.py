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
import yaml
import logging

logger = logging.getLogger('stepfunctions')

def repr_str(dumper, data):
    if '\n' in data:
        return dumper.represent_scalar(u'tag:yaml.org,2002:str', data, style='|')
    return dumper.org_represent_str(data)

yaml.SafeDumper.org_represent_str = yaml.SafeDumper.represent_str
yaml.add_representer(dict, lambda self, data: yaml.representer.SafeRepresenter.represent_dict(self, data.items()), Dumper=yaml.SafeDumper)
yaml.add_representer(str, repr_str, Dumper=yaml.SafeDumper)

CLOUDFORMATION_BASE_TEMPLATE = {
    "AWSTemplateFormatVersion": '2010-09-09',
    "Description": None,
    "Resources": {
        "StateMachineComponent": {
            "Type": "AWS::StepFunctions::StateMachine",
            "Properties": {
                "StateMachineName": None,
                "DefinitionString": None,
                "RoleArn": None,
            }
        }
    }
}

def build_cloudformation_template(workflow):
    logger.warning('To reuse the CloudFormation template in different regions, please make sure to update the region specific AWS resources in the StateMachine definition.')

    template = CLOUDFORMATION_BASE_TEMPLATE.copy()

    template["Description"] = "CloudFormation template for AWS Step Functions - State Machine"
    template["Resources"]["StateMachineComponent"]["Properties"]["StateMachineName"] = workflow.name

    definition = workflow.definition.to_dict()

    template["Resources"]["StateMachineComponent"]["Properties"]["DefinitionString"] = json.dumps(definition, indent=2)
    template["Resources"]["StateMachineComponent"]["Properties"]["RoleArn"] = workflow.role

    return yaml.safe_dump(template, default_flow_style=False)
