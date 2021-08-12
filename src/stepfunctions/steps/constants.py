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
from enum import Enum
from stepfunctions.steps.fields import Field

# Path to SageMaker placeholder parameters
placeholder_paths = {
    # Paths taken from https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_CreateProcessingJob.html
    'ProcessingStep': {
        Field.Role.value: ['RoleArn'],
        Field.ImageUri.value: ['AppSpecification', 'ImageUri'],
        Field.InstanceCount.value: ['ProcessingResources', 'ClusterConfig', 'InstanceCount'],
        Field.InstanceType.value: ['ProcessingResources', 'ClusterConfig', 'InstanceType'],
        Field.Entrypoint.value: ['AppSpecification', 'ContainerEntrypoint'],
        Field.VolumeSizeInGB.value: ['ProcessingResources', 'ClusterConfig', 'VolumeSizeInGB'],
        Field.VolumeKMSKey.value: ['ProcessingResources', 'ClusterConfig', 'VolumeKmsKeyId'],
        Field.Env.value: ['Environment'],
        Field.Tags.value: ['Tags'],
    }
}
