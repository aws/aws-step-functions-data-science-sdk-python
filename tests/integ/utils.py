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

import time

def state_machine_delete_wait(client, state_machine_arn, sleep_interval=10):
    response = client.delete_state_machine(stateMachineArn=state_machine_arn)
    state_machine_status = "DELETING"

    while state_machine_status is not None:
        try:
            state_machine_describe = client.describe_state_machine(stateMachineArn=state_machine_arn)
            state_machine_status = state_machine_describe.get("status")
            time.sleep(sleep_interval)
        except:
            state_machine_status = None

def delete_sagemaker_model(model_name, sagemaker_session):
    sagemaker_session.delete_model(model_name=model_name)

def delete_sagemaker_endpoint_config(endpoint_config_name, sagemaker_session):
    sagemaker_session.delete_endpoint_config(endpoint_config_name=endpoint_config_name)

def delete_sagemaker_endpoint(endpoint_name, sagemaker_session, sleep_interval=10):
    sagemaker_session.wait_for_endpoint(endpoint=endpoint_name, poll=sleep_interval)
    sagemaker_session.delete_endpoint(endpoint_name=endpoint_name)

def get_resource_name_from_arn(arn):
    return arn.split(":")[-1]