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


class Field(Enum):

    # Common fields
    Comment          = 'comment'
    InputPath        = 'input_path'
    OutputPath       = 'output_path'
    Parameters       = 'parameters'
    ResultPath       = 'result_path'
    Next             = 'next'
    Retry            = 'retry'
    Catch            = 'catch'
    Branches         = 'branches'
    End              = 'end'
    Version          = 'version'

    # Pass state fields
    Result           = 'result'

    # Fail state fields
    Error            = 'error'
    Cause            = 'cause'

    # Wait state fields
    Seconds          = 'seconds'
    Timestamp        = 'timestamp'
    SecondsPath      = 'seconds_path'
    TimestampPath    = 'timestamp_path'

    # Choice state fields
    Choices          = 'choices'
    Default          = 'default'

    # Map state fields
    Iterator         = 'iterator'
    ItemsPath        = 'items_path'
    MaxConcurrency   = 'max_concurrency'

    # Task state fields
    Resource             = 'resource'
    TimeoutSeconds       = 'timeout_seconds'
    TimeoutSecondsPath   = 'timeout_seconds_path'
    HeartbeatSeconds     = 'heartbeat_seconds'
    HeartbeatSecondsPath = 'heartbeat_seconds_path'

    # Sagemaker step fields
    # Processing Step: Processor
    Role                = 'role'
    ImageUri            = 'image_uri'
    InstanceCount       = 'instance_count'
    InstanceType        = 'instance_type'
    EntryPoint          = 'entrypoint'
    VolumeSizeInGB      = 'volume_size_in_gb'
    VolumeKMSKey        = 'volume_kms_key'
    OutputKMSKey        = 'output_kms_key'
    MaxRuntimeInSeconds = 'max_runtime_in_seconds'
    Env                 = 'env'
    Tags                = 'tags'

    # Training Step: EstimatorBase
    Data                            = 'data'
    VolumeSize                      = 'volume_size'
    MaxRun                          = 'max_run'
    Subnets                         = 'subnets'
    SecurityGroupIds                = 'security_group_ids'
    ModelUri                        = 'model_uri'
    ModelChannelName                = 'model_channel_name'
    MetricDefinitions               = 'metric_definitions'
    EncryptInterContainerTraffic    = 'encrypt_inter_container_traffic'
    UseSpotInstances                = 'use_spot_instances'
    MaxWait                         = 'max_wait'
    CheckpointS3Uri                 = 'checkpoint_s3_uri'
    CheckpointLocalPath             = 'checkpoint_local_path'
    EnableSagemakerMetrics          = 'enable_sagemaker_metrics'
    EnableNetworkIsolation          = 'enable_network_isolation'
    Environment                     = 'environment'

    # Transform Step: Transformer
    Strategy                        = 'strategy'
    AssembleWith                    = 'assemble_with'
    Accept                          = 'accept'
    MaxConcurrentTransforms         = 'max_concurrent_transforms'
    MaxPayload                      = 'max_payload'

    # Model Step
    ModelData                       = 'model_data'
    Name                            = 'name'
    VpcConfig                       = 'vpc_config'
    ImageConfig                     = 'image_config'

    # TuningStep: Tuner
    ObjectiveMetricName             = 'objective_metric_name '
    HyperparameterRanges            = 'hyperparameter_ranges'
    ObjectiveType                   = 'objective_type'
    MaxJobs                         = 'max_jobs'
    MaxParallelJobs                 = 'max_parallel_jobs'
    EarlyStoppingType               = 'early_stopping_type'

    # Retry and catch fields
    ErrorEquals      = 'error_equals'
    IntervalSeconds  = 'interval_seconds'
    MaxAttempts      = 'max_attempts'
    BackoffRate      = 'backoff_rate'
    NextStep         = 'next_step'
