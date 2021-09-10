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

import os

from stepfunctions.steps import Retry

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
DEFAULT_TIMEOUT_MINUTES = 25

# Default retry strategy for SageMaker steps used in integration tests
SAGEMAKER_RETRY_STRATEGY = Retry(
    error_equals=["SageMaker.AmazonSageMakerException"],
    interval_seconds=5,
    max_attempts=5,
    backoff_rate=2
)