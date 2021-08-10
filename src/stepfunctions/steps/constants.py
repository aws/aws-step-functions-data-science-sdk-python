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
        Field.EntryPoint.value: ['AppSpecification', 'ContainerEntrypoint'],
        Field.VolumeSizeInGB.value: ['ProcessingResources', 'ClusterConfig', 'VolumeSizeInGB'],
        Field.VolumeKMSKey.value: ['ProcessingResources', 'ClusterConfig', 'VolumeKmsKeyId'],
        Field.Env.value: ['Environment'],
        Field.Tags.value: ['Tags'],

    },
    # Paths taken from https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_CreateTransformJob.html
    'TransformStep': {
        Field.InstanceCount.value: ['TransformResources', 'InstanceCount'],
        Field.InstanceType.value: ['TransformResources', 'InstanceType'],
        Field.Strategy.value: ['BatchStrategy'],
        Field.AssembleWith.value: ['TransformOutput', 'AssembleWith'],
        Field.OutputPath.value: ['TransformOutput', 'S3OutputPath'],
        Field.OutputKMSKey.value: ['TransformOutput', 'KmsKeyId'],
        Field.Accept.value: ['TransformOutput', 'Accept'],
        Field.MaxConcurrentTransforms.value: ['MaxConcurrentTransforms'],
        Field.MaxPayload.value: ['MaxPayloadInMB'],
        Field.Tags.value: ['Tags'],
        Field.Env.value: ['Environment'],
        Field.VolumeKMSKey.value: ['TransformResources', 'VolumeKmsKeyId']
    },
    # Paths taken from https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_CreateModel.html
    'ModelStep': {
        Field.ImageUri.value: ['PrimaryContainer', 'Image'],
        Field.ModelData.value: ['PrimaryContainer', 'ModelDataUrl'],
        Field.Role.value: ['ExecutionRoleArn'],
        Field.Env.value:  ['PrimaryContainer', 'Environment'],
        Field.Name.value: ['ModelName'],
        Field.VpcConfig.value: ['VpcConfig'],
        Field.EnableNetworkIsolation.value: ['EnableNetworkIsolation'],
        Field.ImageConfig.value: ['PrimaryContainer', 'ImageConfig'],
        Field.Tags.value: ['Tags'],
    },
    # Paths taken from https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_CreateHyperParameterTuningJob.html
    'TuningStep': {
        Field.ObjectiveMetricName.value: ['HyperParameterTuningJobConfig', 'HyperParameterTuningJobObjective',
                                          'MetricName'],
        Field.HyperparameterRanges.value: ['HyperParameterRanges'],
        # TODO - carolngu: metric_definitions - list of 1 elem or multiple -> TrainingJobDefinition vs TrainingJobDefinitions
        Field.Strategy.value: ['Strategy'],
        Field.ObjectiveType.value: ['HyperParameterTuningJobConfig', 'HyperParameterTuningJobObjective', 'Type'],
        Field.MaxJobs.value: ['ResourceLimits', 'MaxNumberOfTrainingJobs'],
        Field.MaxParallelJobs.value: ['ResourceLimits', 'MaxParallelTrainingJobs'],
        Field.Tags.value: ['Tags'],
        Field.EarlyStoppingType.value: ['TrainingJobEarlyStoppingType'],

    },
    # Paths taken from https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_CreateTrainingJob.html
    'TrainingStep': {
        Field.Role.value: ['RoleArn'],
        Field.InstanceCount.value: ['ResourceConfig', 'InstanceCount'],
        Field.InstanceType.value: ['ResourceConfig', 'InstanceType'],
        Field.VolumeSize.value: ['ResourceConfig', 'VolumeSizeInGB'],
        Field.VolumeKMSKey.value: ['ResourceConfig', 'VolumeKmsKeyId'],
        Field.MaxRun.value: ['StoppingCondition', 'MaxRuntimeInSeconds'],
        Field.OutputKMSKey.value: ['OutputDataConfig', 'KmsKeyId'],
        Field.Subnets.value: ['VpcConfig', 'Subnets'],
        Field.SecurityGroupIds.value: ['VpcConfig', 'SecurityGroupIds'],
        Field.MetricDefinitions.value: ['AlgorithmSpecification', 'MetricDefinitions'],
        Field.EncryptInterContainerTraffic.value: ['EnableInterContainerTrafficEncryption'],
        Field.UseSpotInstances.value: ['EnableManagedSpotTraining'],
        Field.MaxWait.value: ['StoppingCondition', 'MaxWaitTimeInSeconds'],
        Field.CheckpointS3Uri.value: ['CheckpointConfig', 'S3Uri'],
        Field.CheckpointLocalPath.value: ['CheckpointConfig', 'LocalPath'],
        Field.EnableSagemakerMetrics.value: ['AlgorithmSpecification', 'EnableSageMakerMetricsTimeSeries'],
        Field.EnableNetworkIsolation.value: ['EnableNetworkIsolation'],
        Field.Environment.value: ['Environment'],
        Field.Tags.value: ['Tags'],
    }
}
