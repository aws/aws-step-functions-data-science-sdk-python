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

import botocore

boto_true_api_call = botocore.client.BaseClient._make_api_call

def mock_boto_api_call(self, operation_name, kwarg):
    if operation_name == "GetCallerIdentity":
        return {
            "Account": "ABCXYZ"
        }
    elif operation_name == "CreateBucket":
        return {
            "Location": "s3://abcxyz-path/"
        }
    return boto_true_api_call(self, operation_name, kwarg)