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


def replace_parameters_with_context_object(step):
    """Replace the parameters using $$.Execution.Input."""
    updated_parameters = {}
    for k in step.parameters.keys():
        updated_parameters['{key}.$'.format(key=k)] = "$$.Execution.Input['{state_id}'].{key}".format(state_id=step.state_id, key=k)
    return updated_parameters

def replace_parameters_with_jsonpath(step, params):

    def search_and_replace(src_params, dest_params, key):
        """Search and replace the dict entry in-place."""
        original_key = key[:-2] # Remove .$ in the end
        del src_params[original_key]
        src_params[key] = dest_params[key]

    def replace_values(src_params, dest_params):
        if isinstance(dest_params, dict):
            for key in dest_params.keys():
                if key.endswith('$'):
                    search_and_replace(src_params, dest_params, key)
                else:
                    replace_values(src_params[key], dest_params[key])
    
    task_parameters = step.parameters.copy()
    replace_values(task_parameters, params)
    
    return task_parameters
