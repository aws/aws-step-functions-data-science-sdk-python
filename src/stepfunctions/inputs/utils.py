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

def flatten(input, parent_key='', sep='.'):
    items = []
    for k, v in input.items():
        if parent_key:
            flattened_key = parent_key + sep + k
        else:
            flattened_key = k
        if isinstance(v, dict):
            items.extend(flatten(v, flattened_key, sep=sep).items())
        else:
            items.append((flattened_key, v))
    return dict(items)

def replace_type_with_str(schema):
    schema_with_str = {}
    for k,v in schema.items():
        if isinstance(v, dict):
            schema_with_str[k] = replace_type_with_str(v)
        else:
            schema_with_str[k] = v.__name__
    return schema_with_str