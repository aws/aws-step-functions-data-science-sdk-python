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

import pytest
import boto3

from unittest.mock import Mock, patch
from stepfunctions.workflow.utils import append_user_agent_to_client

@pytest.fixture
def client():
    sfn = boto3.client('stepfunctions')
    sfn._client_config = Mock()
    sfn._client_config.user_agent = "abc/1.2.3 def/4.5.6"
    return sfn

@patch('stepfunctions.__useragent__', 'helloworld')
@patch('stepfunctions.__version__', '9.8.7')
def test_append_user_agent_to_client(client):
    append_user_agent_to_client(client)
    user_agent_suffix = client._client_config.user_agent.split()[-1]
    assert user_agent_suffix == "helloworld/9.8.7"
    