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

import boto3
import logging

logger = logging.getLogger('stepfunctions')


def tags_dict_to_kv_list(tags_dict):
    kv_list = [{"Key": k, "Value": v} for k, v in tags_dict.items()]
    return kv_list


def get_aws_partition():

    """
    Returns the aws partition for the current boto3 session.
    Defaults to 'aws' if the region could not be detected.
    """

    partitions = boto3.session.Session().get_available_partitions()
    cur_region = boto3.session.Session().region_name
    cur_partition = "aws"

    if cur_region is None:
        logger.warning("No region detected for the boto3 session. Using default partition: aws")
        return cur_partition

    for partition in partitions:
        regions = boto3.session.Session().get_available_regions("stepfunctions", partition)
        if cur_region in regions:
            cur_partition = partition
            return cur_partition

    return cur_partition
