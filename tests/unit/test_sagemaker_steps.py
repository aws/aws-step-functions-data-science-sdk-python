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
import sagemaker
import boto3

from sagemaker.transformer import Transformer
from sagemaker.model import Model
from sagemaker.tensorflow import TensorFlow
from sagemaker.pipeline import PipelineModel
from sagemaker.model_monitor import DataCaptureConfig
from sagemaker.debugger import Rule, rule_configs, DebuggerHookConfig, CollectionConfig
from sagemaker.sklearn.processing import SKLearnProcessor
from sagemaker.processing import ProcessingInput, ProcessingOutput

from unittest.mock import MagicMock, patch
from stepfunctions.inputs import ExecutionInput, StepInput
from stepfunctions.steps.fields import Field
from stepfunctions.steps.sagemaker import TrainingStep, TransformStep, ModelStep, EndpointStep, EndpointConfigStep,\
    ProcessingStep
from stepfunctions.steps.sagemaker import tuning_config

from tests.unit.utils import mock_boto_api_call

EXECUTION_ROLE = 'execution-role'
PCA_IMAGE = '382416733822.dkr.ecr.us-east-1.amazonaws.com/pca:1'
TENSORFLOW_IMAGE = '520713654638.dkr.ecr.us-east-1.amazonaws.com/sagemaker-tensorflow:1.13-gpu-py2'
DEFAULT_TAGS = {'Purpose': 'unittests'}
DEFAULT_TAGS_LIST = [{'Key': 'Purpose', 'Value': 'unittests'}]


@pytest.fixture
def pca_estimator():
    s3_output_location = 's3://sagemaker/models'

    pca = sagemaker.estimator.Estimator(
        PCA_IMAGE,
        role=EXECUTION_ROLE,
        instance_count=1,
        instance_type='ml.c4.xlarge',
        output_path=s3_output_location
    )

    pca.set_hyperparameters(
        feature_dim=50000,
        num_components=10,
        subtract_mean=True,
        algorithm_mode='randomized',
        mini_batch_size=200
    )

    pca.sagemaker_session = MagicMock()
    pca.sagemaker_session.boto_region_name = 'us-east-1'
    pca.sagemaker_session._default_bucket = 'sagemaker'

    return pca


@pytest.fixture
def pca_estimator_with_env():
    s3_output_location = 's3://sagemaker/models'

    pca = sagemaker.estimator.Estimator(
        PCA_IMAGE,
        role=EXECUTION_ROLE,
        instance_count=1,
        instance_type='ml.c4.xlarge',
        output_path=s3_output_location,
        environment={
            'JobName': "job_name",
            'ModelName': "model_name"
        },
        subnets=[
            'subnet-00000000000000000',
            'subnet-00000000000000001'
        ]
    )

    pca.set_hyperparameters(
        feature_dim=50000,
        num_components=10,
        subtract_mean=True,
        algorithm_mode='randomized',
        mini_batch_size=200
    )

    pca.sagemaker_session = MagicMock()
    pca.sagemaker_session.boto_region_name = 'us-east-1'
    pca.sagemaker_session._default_bucket = 'sagemaker'

    return pca


@pytest.fixture
def pca_estimator_with_debug_hook():
    s3_output_location = 's3://sagemaker/models'

    hook_config = DebuggerHookConfig(
        s3_output_path='s3://sagemaker/output/debug',
        hook_parameters={
            "save_interval": "1"
        },
        collection_configs=[
            CollectionConfig("hyperparameters"),
            CollectionConfig("metrics")
        ]
    )

    rules = [Rule.sagemaker(rule_configs.confusion(),
        rule_parameters={
            "category_no": "15",
            "min_diag": "0.7",
            "max_off_diag": "0.3",
            "start_step": "17",
            "end_step": "19"}
    )]

    pca = sagemaker.estimator.Estimator(
        PCA_IMAGE,
        role=EXECUTION_ROLE,
        instance_count=1,
        instance_type='ml.c4.xlarge',
        output_path=s3_output_location,
        debugger_hook_config = hook_config,
        rules=rules
    )

    pca.set_hyperparameters(
        feature_dim=50000,
        num_components=10,
        subtract_mean=True,
        algorithm_mode='randomized',
        mini_batch_size=200
    )

    pca.sagemaker_session = MagicMock()
    pca.sagemaker_session.boto_region_name = 'us-east-1'
    pca.sagemaker_session._default_bucket = 'sagemaker'

    return pca


@pytest.fixture
def pca_estimator_with_falsy_debug_hook():
    s3_output_location = 's3://sagemaker/models'

    pca = sagemaker.estimator.Estimator(
        PCA_IMAGE,
        role=EXECUTION_ROLE,
        instance_count=1,
        instance_type='ml.c4.xlarge',
        output_path=s3_output_location,
        debugger_hook_config = False
    )

    pca.set_hyperparameters(
        feature_dim=50000,
        num_components=10,
        subtract_mean=True,
        algorithm_mode='randomized',
        mini_batch_size=200
    )

    pca.sagemaker_session = MagicMock()
    pca.sagemaker_session.boto_region_name = 'us-east-1'
    pca.sagemaker_session._default_bucket = 'sagemaker'

    return pca


@pytest.fixture
def pca_model():
    model_data = 's3://sagemaker/models/pca.tar.gz'
    return Model(
        model_data=model_data,
        image_uri=PCA_IMAGE,
        role=EXECUTION_ROLE,
        name='pca-model'
    )


@pytest.fixture
def pca_model_with_env():
    model_data = 's3://sagemaker/models/pca.tar.gz'
    return Model(
        model_data=model_data,
        image_uri=PCA_IMAGE,
        role=EXECUTION_ROLE,
        name='pca-model',
        env={
            'JobName': "job_name",
            'ModelName': "model_name"
        },
        vpc_config={
            "SecurityGroupIds": ["sg-00000000000000000"],
            "Subnets": ["subnet-00000000000000000", "subnet-00000000000000001"]
        },
        image_config={
            "RepositoryAccessMode": "Vpc",
            "RepositoryAuthConfig": {
                "RepositoryCredentialsProviderArn": "arn"
            }
        }
    )


@pytest.fixture
def pca_transformer(pca_model):
    return Transformer(
        model_name='pca-model',
        instance_count=1,
        instance_type='ml.c4.xlarge',
        output_path='s3://sagemaker/transform-output'
    )


@pytest.fixture
def tensorflow_estimator():
    s3_output_location = 's3://sagemaker/models'
    s3_source_location = 's3://sagemaker/source'

    estimator = TensorFlow(
        entry_point='tf_train.py',
        role=EXECUTION_ROLE,
        framework_version='1.13',
        instance_count=1,
        instance_type='ml.p2.xlarge',
        output_path=s3_output_location,
        source_dir=s3_source_location,
        image_uri=TENSORFLOW_IMAGE,
        model_dir=False,
        hyperparameters={
            'training_steps': 1000,
            'evaluation_steps': 100,
            'checkpoint_path': 's3://sagemaker/models/sagemaker-tensorflow/checkpoints',
        }
    )

    estimator.debugger_hook_config = DebuggerHookConfig(
        s3_output_path='s3://sagemaker/models/debug'
    )

    estimator.sagemaker_session = MagicMock()
    estimator.sagemaker_session.boto_region_name = 'us-east-1'
    estimator.sagemaker_session._default_bucket = 'sagemaker'

    return estimator


@pytest.fixture
def sklearn_processor():
    sagemaker_session = MagicMock()
    sagemaker_session.boto_region_name = 'us-east-1'
    sagemaker_session._default_bucket = 'sagemaker'

    processor = SKLearnProcessor(
        framework_version="0.20.0",
        role=EXECUTION_ROLE,
        instance_type="ml.m5.xlarge",
        instance_count=1,
        sagemaker_session=sagemaker_session
    )

    return processor


@patch('botocore.client.BaseClient._make_api_call', new=mock_boto_api_call)
@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_training_step_creation(pca_estimator):
    step = TrainingStep('Training',
        estimator=pca_estimator,
        job_name='TrainingJob',
        experiment_config={
            'ExperimentName': 'pca_experiment',
            'TrialName': 'pca_trial',
            'TrialComponentDisplayName': 'Training'
        },
        output_data_config_path='s3://sagemaker-us-east-1-111111111111',
        tags=DEFAULT_TAGS,
    )
    assert step.to_dict() == {
        'Type': 'Task',
        'Parameters': {
            'AlgorithmSpecification': {
                'TrainingImage': PCA_IMAGE,
                'TrainingInputMode': 'File'
            },
            'OutputDataConfig': {
                'S3OutputPath': 's3://sagemaker-us-east-1-111111111111'
            },
            'StoppingCondition': {
                'MaxRuntimeInSeconds': 86400
            },
            'ResourceConfig': {
                'InstanceCount': 1,
                'InstanceType': 'ml.c4.xlarge',
                'VolumeSizeInGB': 30
            },
            'RoleArn': EXECUTION_ROLE,
            'HyperParameters': {
                'feature_dim': '50000',
                'num_components': '10',
                'subtract_mean': 'True',
                'algorithm_mode': 'randomized',
                'mini_batch_size': '200'
            },
            'ExperimentConfig': {
                'ExperimentName': 'pca_experiment',
                'TrialName': 'pca_trial',
                'TrialComponentDisplayName': 'Training'
            },
            'TrainingJobName': 'TrainingJob',
            'Tags': DEFAULT_TAGS_LIST
        },
        'Resource': 'arn:aws:states:::sagemaker:createTrainingJob.sync',
        'End': True
    }


@patch('botocore.client.BaseClient._make_api_call', new=mock_boto_api_call)
@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_training_step_creation_with_placeholders(pca_estimator):
    execution_input = ExecutionInput(schema={
        'Data': str,
        'OutputPath': str,
        'HyperParameters': str,
        'ExperimentConfig': str,
        'Tags': str,
        'InstanceCount': int,
        'InstanceType': str,
        'MaxRun': int,
        'MetricDefinitions': str,
        'MaxWait': int,
        'CheckpointS3Uri': str,
        'CheckpointLocalPath': str,
        'EnableSagemakerMetrics': bool,
        'EnableNetworkIsolation': bool,
        'Environment': str
    })

    step_input = StepInput(schema={
        'JobName': str,
    })

    parameters = {
            'AlgorithmSpecification': {
                'TrainingImage': PCA_IMAGE,
                'TrainingInputMode': 'File',
                'MetricDefinitions': execution_input['MetricDefinitions'],
                'EnableSageMakerMetricsTimeSeries': execution_input['EnableSagemakerMetrics']
            },
            'CheckpointConfig': {
                'S3Uri': execution_input['CheckpointS3Uri'],
                'LocalPath': execution_input['CheckpointLocalPath']
            },
            'EnableNetworkIsolation': execution_input['EnableNetworkIsolation'],
            'StoppingCondition': {
                'MaxRuntimeInSeconds': execution_input['MaxRun'],
                'MaxWaitTimeInSeconds': execution_input['MaxWait']
            },
            'ResourceConfig': {
                'InstanceCount': execution_input['InstanceCount'],
                'InstanceType': execution_input['InstanceType']
            },
            'Environment': execution_input['Environment'],
            'ExperimentConfig': execution_input['ExperimentConfig']
        }

    step = TrainingStep('Training',
        estimator=pca_estimator,
        job_name=step_input['JobName'],
        data=execution_input['Data'],
        output_data_config_path=execution_input['OutputPath'],
        experiment_config=execution_input['ExperimentConfig'],
        tags=execution_input['Tags'],
        mini_batch_size=1000,
        hyperparameters=execution_input['HyperParameters'],
        parameters=parameters
    )
    assert step.to_dict()['Parameters'] == {
        'AlgorithmSpecification': {
            'EnableSageMakerMetricsTimeSeries.$': "$$.Execution.Input['EnableSagemakerMetrics']",
            'MetricDefinitions.$': "$$.Execution.Input['MetricDefinitions']",
            'TrainingImage': PCA_IMAGE,
            'TrainingInputMode': 'File'
        },
        'CheckpointConfig': {'LocalPath.$': "$$.Execution.Input['CheckpointLocalPath']",
                             'S3Uri.$': "$$.Execution.Input['CheckpointS3Uri']"},
        'EnableNetworkIsolation.$': "$$.Execution.Input['EnableNetworkIsolation']",
        'Environment.$': "$$.Execution.Input['Environment']",
        'OutputDataConfig': {
            'S3OutputPath.$': "$$.Execution.Input['OutputPath']"
        },
        'StoppingCondition': {
            'MaxRuntimeInSeconds.$': "$$.Execution.Input['MaxRun']",
            'MaxWaitTimeInSeconds.$': "$$.Execution.Input['MaxWait']"
        },
        'ResourceConfig': {
            'InstanceCount.$': "$$.Execution.Input['InstanceCount']",
            'InstanceType.$': "$$.Execution.Input['InstanceType']",
            'VolumeSizeInGB': 30
        },
        'RoleArn': EXECUTION_ROLE,
        'HyperParameters.$': "$$.Execution.Input['HyperParameters']",
        'InputDataConfig': [
            {
                'ChannelName': 'training',
                'DataSource': {
                    'S3DataSource': {
                        'S3DataDistributionType': 'FullyReplicated',
                        'S3DataType': 'S3Prefix',
                        'S3Uri.$': "$$.Execution.Input['Data']"
                    }
                }
            }
        ],
        'ExperimentConfig.$': "$$.Execution.Input['ExperimentConfig']",
        'TrainingJobName.$': "$['JobName']",
        'Tags.$': "$$.Execution.Input['Tags']"
    }


@patch('botocore.client.BaseClient._make_api_call', new=mock_boto_api_call)
@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_training_step_creation_with_hyperparameters_containing_placeholders(pca_estimator):
    execution_input = ExecutionInput(schema={
        'Data': str,
        'OutputPath': str,
        'num_components': str,
        'HyperParamA': str,
        'HyperParamB': str,
    })

    step_input = StepInput(schema={
        'JobName': str,
    })

    step = TrainingStep('Training',
        estimator=pca_estimator,
        job_name=step_input['JobName'],
        data=execution_input['Data'],
        output_data_config_path=execution_input['OutputPath'],
        experiment_config={
            'ExperimentName': 'pca_experiment',
            'TrialName': 'pca_trial',
            'TrialComponentDisplayName': 'Training'
        },
        tags=DEFAULT_TAGS,
        hyperparameters={
            'num_components': execution_input['num_components'],  # This will overwrite the value that was defined in the pca_estimator
            'HyperParamA': execution_input['HyperParamA'],
            'HyperParamB': execution_input['HyperParamB']
        }
    )
    assert step.to_dict()['Parameters']['HyperParameters'] == {
        'HyperParamA.$': "$$.Execution.Input['HyperParamA']",
        'HyperParamB.$': "$$.Execution.Input['HyperParamB']",
        'algorithm_mode': 'randomized',
        'feature_dim': 50000,
        'mini_batch_size': 200,
        'num_components.$': "$$.Execution.Input['num_components']",
        'subtract_mean': True
    }


@patch('botocore.client.BaseClient._make_api_call', new=mock_boto_api_call)
@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_training_step_creation_with_debug_hook(pca_estimator_with_debug_hook):
    step = TrainingStep('Training',
        estimator=pca_estimator_with_debug_hook,
        job_name='TrainingJob')
    assert step.to_dict() == {
        'Type': 'Task',
        'Parameters': {
            'AlgorithmSpecification': {
                'TrainingImage': PCA_IMAGE,
                'TrainingInputMode': 'File'
            },
            'OutputDataConfig': {
                'S3OutputPath': 's3://sagemaker/models'
            },
            'StoppingCondition': {
                'MaxRuntimeInSeconds': 86400
            },
            'ResourceConfig': {
                'InstanceCount': 1,
                'InstanceType': 'ml.c4.xlarge',
                'VolumeSizeInGB': 30
            },
            'RoleArn': EXECUTION_ROLE,
            'HyperParameters': {
                'feature_dim': '50000',
                'num_components': '10',
                'subtract_mean': 'True',
                'algorithm_mode': 'randomized',
                'mini_batch_size': '200'
            },
            'DebugHookConfig': {
                'S3OutputPath': 's3://sagemaker/output/debug',
                'HookParameters': {'save_interval': '1'},
                'CollectionConfigurations': [
                    {'CollectionName': 'hyperparameters'},
                    {'CollectionName': 'metrics'}
                ]
            },
            'DebugRuleConfigurations': [
                {
                    'RuleConfigurationName': 'Confusion',
                    'RuleEvaluatorImage': '503895931360.dkr.ecr.us-east-1.amazonaws.com/sagemaker-debugger-rules:latest',
                    'RuleParameters': {
                        'rule_to_invoke': 'Confusion',
                        'category_no': '15',
                        'min_diag': '0.7',
                        'max_off_diag': '0.3',
                        'start_step': '17',
                        'end_step': '19'
                    }
                }
            ],
            'TrainingJobName': 'TrainingJob'
        },
        'Resource': 'arn:aws:states:::sagemaker:createTrainingJob.sync',
        'End': True
    }


@patch('botocore.client.BaseClient._make_api_call', new=mock_boto_api_call)
@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_training_step_creation_with_falsy_debug_hook(pca_estimator_with_falsy_debug_hook):
    step = TrainingStep('Training',
        estimator=pca_estimator_with_falsy_debug_hook,
        job_name='TrainingJob')
    assert step.to_dict() == {
        'Type': 'Task',
        'Parameters': {
            'AlgorithmSpecification': {
                'TrainingImage': PCA_IMAGE,
                'TrainingInputMode': 'File'
            },
            'OutputDataConfig': {
                'S3OutputPath': 's3://sagemaker/models'
            },
            'StoppingCondition': {
                'MaxRuntimeInSeconds': 86400
            },
            'ResourceConfig': {
                'InstanceCount': 1,
                'InstanceType': 'ml.c4.xlarge',
                'VolumeSizeInGB': 30
            },
            'RoleArn': EXECUTION_ROLE,
            'HyperParameters': {
                'feature_dim': '50000',
                'num_components': '10',
                'subtract_mean': 'True',
                'algorithm_mode': 'randomized',
                'mini_batch_size': '200'
            },
            'TrainingJobName': 'TrainingJob'
        },
        'Resource': 'arn:aws:states:::sagemaker:createTrainingJob.sync',
        'End': True
    }


@patch('botocore.client.BaseClient._make_api_call', new=mock_boto_api_call)
@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_training_step_creation_with_model(pca_estimator):
    training_step = TrainingStep('Training', estimator=pca_estimator, job_name='TrainingJob')
    model_step = ModelStep('Training - Save Model', training_step.get_expected_model(model_name=training_step.output()['TrainingJobName']))
    training_step.next(model_step)
    assert training_step.to_dict() == {
        'Type': 'Task',
        'Parameters': {
            'AlgorithmSpecification': {
                'TrainingImage': PCA_IMAGE,
                'TrainingInputMode': 'File'
            },
            'OutputDataConfig': {
                'S3OutputPath': 's3://sagemaker/models'
            },
            'StoppingCondition': {
                'MaxRuntimeInSeconds': 86400
            },
            'ResourceConfig': {
                'InstanceCount': 1,
                'InstanceType': 'ml.c4.xlarge',
                'VolumeSizeInGB': 30
            },
            'RoleArn': EXECUTION_ROLE,
            'HyperParameters': {
                'feature_dim': '50000',
                'num_components': '10',
                'subtract_mean': 'True',
                'algorithm_mode': 'randomized',
                'mini_batch_size': '200'
            },
            'TrainingJobName': 'TrainingJob'
        },
        'Resource': 'arn:aws:states:::sagemaker:createTrainingJob.sync',
        'Next': 'Training - Save Model'
    }

    assert model_step.to_dict() == {
        'Type': 'Task',
        'Resource': 'arn:aws:states:::sagemaker:createModel',
        'Parameters': {
            'ExecutionRoleArn': EXECUTION_ROLE,
            'ModelName.$': "$['TrainingJobName']",
            'PrimaryContainer': {
                'Environment': {},
                'Image': PCA_IMAGE,
                'ModelDataUrl.$': "$['ModelArtifacts']['S3ModelArtifacts']"
            }
        },
        'End': True
    }


@patch('botocore.client.BaseClient._make_api_call', new=mock_boto_api_call)
@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_training_step_creation_with_model_with_env(pca_estimator_with_env):
    training_step = TrainingStep('Training', estimator=pca_estimator_with_env, job_name='TrainingJob')
    model_step = ModelStep('Training - Save Model', training_step.get_expected_model(model_name=training_step.output()['TrainingJobName']))
    training_step.next(model_step)
    assert training_step.to_dict() == {
        'Type': 'Task',
        'Parameters': {
            'AlgorithmSpecification': {
                'TrainingImage': PCA_IMAGE,
                'TrainingInputMode': 'File'
            },
            'OutputDataConfig': {
                'S3OutputPath': 's3://sagemaker/models'
            },
            'StoppingCondition': {
                'MaxRuntimeInSeconds': 86400
            },
            'ResourceConfig': {
                'InstanceCount': 1,
                'InstanceType': 'ml.c4.xlarge',
                'VolumeSizeInGB': 30
            },
            'RoleArn': EXECUTION_ROLE,
            'HyperParameters': {
                'feature_dim': '50000',
                'num_components': '10',
                'subtract_mean': 'True',
                'algorithm_mode': 'randomized',
                'mini_batch_size': '200'
            },
            'TrainingJobName': 'TrainingJob'
        },
        'Resource': 'arn:aws:states:::sagemaker:createTrainingJob.sync',
        'Next': 'Training - Save Model'
    }

    assert model_step.to_dict() == {
        'Type': 'Task',
        'Resource': 'arn:aws:states:::sagemaker:createModel',
        'Parameters': {
            'ExecutionRoleArn': EXECUTION_ROLE,
            'ModelName.$': "$['TrainingJobName']",
            'PrimaryContainer': {
                'Environment': {
                    'JobName': 'job_name',
                    'ModelName': 'model_name'
                },
                'Image': PCA_IMAGE,
                'ModelDataUrl.$': "$['ModelArtifacts']['S3ModelArtifacts']"
            }
        },
        'End': True
    }


@patch('botocore.client.BaseClient._make_api_call', new=mock_boto_api_call)
@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_training_step_creation_with_framework(tensorflow_estimator):
    step = TrainingStep('Training',
        estimator=tensorflow_estimator,
        data={'train': 's3://sagemaker/train'},
        job_name='tensorflow-job',
        mini_batch_size=1024,
        tags=DEFAULT_TAGS,
    )

    assert step.to_dict() == {
        'Type': 'Task',
        'Parameters': {
            'AlgorithmSpecification': {
                'TrainingImage': TENSORFLOW_IMAGE,
                'TrainingInputMode': 'File'
            },
            'InputDataConfig': [
                {
                    'DataSource': {
                        'S3DataSource': {
                            'S3DataDistributionType': 'FullyReplicated',
                            'S3DataType': 'S3Prefix',
                            'S3Uri': 's3://sagemaker/train'
                        }
                    },
                    'ChannelName': 'train'
                }
            ],
            'OutputDataConfig': {
                'S3OutputPath': 's3://sagemaker/models'
            },
            'DebugHookConfig': {
                'S3OutputPath': 's3://sagemaker/models/debug'
            },
            'StoppingCondition': {
                'MaxRuntimeInSeconds': 86400
            },
            'ResourceConfig': {
                'InstanceCount': 1,
                'InstanceType': 'ml.p2.xlarge',
                'VolumeSizeInGB': 30
            },
            'RoleArn': EXECUTION_ROLE,
            'HyperParameters': {
                'checkpoint_path': '"s3://sagemaker/models/sagemaker-tensorflow/checkpoints"',
                'evaluation_steps': '100',
                'sagemaker_container_log_level': '20',
                'sagemaker_job_name': '"tensorflow-job"',
                'sagemaker_program': '"tf_train.py"',
                'sagemaker_region': '"us-east-1"',
                'sagemaker_submit_directory': '"s3://sagemaker/source"',
                'training_steps': '1000',
            },
            'TrainingJobName': 'tensorflow-job',
            'Tags': DEFAULT_TAGS_LIST

        },
        'Resource': 'arn:aws:states:::sagemaker:createTrainingJob.sync',
        'End': True
    }

@patch('botocore.client.BaseClient._make_api_call', new=mock_boto_api_call)
@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_training_step_merges_hyperparameters_from_constructor_and_estimator(tensorflow_estimator):
    step = TrainingStep('Training',
        estimator=tensorflow_estimator,
        data={'train': 's3://sagemaker/train'},
        job_name='tensorflow-job',
        mini_batch_size=1024,
        hyperparameters={
            'key': 'value'
        }
    )

    assert step.to_dict() == {
        'Type': 'Task',
        'Parameters': {
            'AlgorithmSpecification': {
                'TrainingImage': TENSORFLOW_IMAGE,
                'TrainingInputMode': 'File'
            },
            'InputDataConfig': [
                {
                    'DataSource': {
                        'S3DataSource': {
                            'S3DataDistributionType': 'FullyReplicated',
                            'S3DataType': 'S3Prefix',
                            'S3Uri': 's3://sagemaker/train'
                        }
                    },
                    'ChannelName': 'train'
                }
            ],
            'OutputDataConfig': {
                'S3OutputPath': 's3://sagemaker/models'
            },
            'DebugHookConfig': {
                'S3OutputPath': 's3://sagemaker/models/debug'
            },
            'StoppingCondition': {
                'MaxRuntimeInSeconds': 86400
            },
            'ResourceConfig': {
                'InstanceCount': 1,
                'InstanceType': 'ml.p2.xlarge',
                'VolumeSizeInGB': 30
            },
            'RoleArn': EXECUTION_ROLE,
            'HyperParameters': {
                'checkpoint_path': '"s3://sagemaker/models/sagemaker-tensorflow/checkpoints"',
                'evaluation_steps': '100',
                'key': 'value',
                'sagemaker_container_log_level': '20',
                'sagemaker_job_name': '"tensorflow-job"',
                'sagemaker_program': '"tf_train.py"',
                'sagemaker_region': '"us-east-1"',
                'sagemaker_submit_directory': '"s3://sagemaker/source"',
                'training_steps': '1000',
            },
            'TrainingJobName': 'tensorflow-job',
        },
        'Resource': 'arn:aws:states:::sagemaker:createTrainingJob.sync',
        'End': True
}


@patch('botocore.client.BaseClient._make_api_call', new=mock_boto_api_call)
@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_training_step_uses_constructor_hyperparameters_when_duplicates_supplied_in_estimator(tensorflow_estimator):
    step = TrainingStep('Training',
        estimator=tensorflow_estimator,
        data={'train': 's3://sagemaker/train'},
        job_name='tensorflow-job',
        mini_batch_size=1024,
        hyperparameters={
            # set as 1000 in estimator
            'training_steps': '500'
        }
    )

    assert step.to_dict() == {
        'Type': 'Task',
        'Parameters': {
            'AlgorithmSpecification': {
                'TrainingImage': TENSORFLOW_IMAGE,
                'TrainingInputMode': 'File'
            },
            'InputDataConfig': [
                {
                    'DataSource': {
                        'S3DataSource': {
                            'S3DataDistributionType': 'FullyReplicated',
                            'S3DataType': 'S3Prefix',
                            'S3Uri': 's3://sagemaker/train'
                        }
                    },
                    'ChannelName': 'train'
                }
            ],
            'OutputDataConfig': {
                'S3OutputPath': 's3://sagemaker/models'
            },
            'DebugHookConfig': {
                'S3OutputPath': 's3://sagemaker/models/debug'
            },
            'StoppingCondition': {
                'MaxRuntimeInSeconds': 86400
            },
            'ResourceConfig': {
                'InstanceCount': 1,
                'InstanceType': 'ml.p2.xlarge',
                'VolumeSizeInGB': 30
            },
            'RoleArn': EXECUTION_ROLE,
            'HyperParameters': {
                'checkpoint_path': '"s3://sagemaker/models/sagemaker-tensorflow/checkpoints"',
                'evaluation_steps': '100',
                'sagemaker_container_log_level': '20',
                'sagemaker_job_name': '"tensorflow-job"',
                'sagemaker_program': '"tf_train.py"',
                'sagemaker_region': '"us-east-1"',
                'sagemaker_submit_directory': '"s3://sagemaker/source"',
                'training_steps': '500',
            },
            'TrainingJobName': 'tensorflow-job',
        },
        'Resource': 'arn:aws:states:::sagemaker:createTrainingJob.sync',
        'End': True
    }


@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_transform_step_creation(pca_transformer):
    step = TransformStep('Inference',
        transformer=pca_transformer,
        data='s3://sagemaker/inference',
        job_name='transform-job',
        model_name='pca-model',
        experiment_config={
            'ExperimentName': 'pca_experiment',
            'TrialName': 'pca_trial',
            'TrialComponentDisplayName': 'Transform'
        },
        tags=DEFAULT_TAGS,
        join_source='Input',
        output_filter='$[2:]',
        input_filter='$[1:]'
    )
    assert step.to_dict() == {
        'Type': 'Task',
        'Parameters': {
            'ModelName': 'pca-model',
            'TransformInput': {
                'DataSource': {
                    'S3DataSource': {
                        'S3DataType': 'S3Prefix',
                        'S3Uri': 's3://sagemaker/inference'
                    }
                }
            },
            'TransformOutput': {
                'S3OutputPath': 's3://sagemaker/transform-output'
            },
            'TransformJobName': 'transform-job',
            'TransformResources': {
                'InstanceCount': 1,
                'InstanceType': 'ml.c4.xlarge'
            },
            'ExperimentConfig': {
                'ExperimentName': 'pca_experiment',
                'TrialName': 'pca_trial',
                'TrialComponentDisplayName': 'Transform'
            },
            'DataProcessing': {
                'InputFilter': '$[1:]',
                'OutputFilter': '$[2:]',
                'JoinSource': 'Input',
            },
            'Tags': DEFAULT_TAGS_LIST
        },
        'Resource': 'arn:aws:states:::sagemaker:createTransformJob.sync',
        'End': True
    }


@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_transform_step_creation_with_placeholder(pca_transformer):
    execution_input = ExecutionInput(schema={
        'data': str,
        'data_type': str,
        'content_type': str,
        'compression_type': str,
        'split_type': str,
        'input_filter': str,
        'output_filter': str,
        'join_source': str,
        'job_name': str,
        'model_name': str,
        'instance_count': int,
        'strategy': str,
        'assemble_with': str,
        'output_path': str,
        'output_kms_key': str,
        'accept': str,
        'max_concurrent_transforms': int,
        'max_payload': int,
        'tags': [{str: str}],
        'env': str,
        'volume_kms_key': str,
        'experiment_config': str,
    })

    step_input = StepInput(schema={
        'instance_type': str
    })

    parameters = {
            'BatchStrategy': execution_input['strategy'],
            'TransformOutput': {
                'Accept': execution_input['accept'],
                'AssembleWith': execution_input['assemble_with'],
                'KmsKeyId': execution_input['output_kms_key'],
                'S3OutputPath': execution_input['output_path']
            },
            'TransformResources': {
                'InstanceCount': execution_input['instance_count'],
                'InstanceType': step_input['instance_type'],
                'VolumeKmsKeyId': execution_input['volume_kms_key']
            },
            'ExperimentConfig': execution_input['experiment_config'],
            'Tags': execution_input['tags'],
            'Environment': execution_input['env'],
            'MaxConcurrentTransforms': execution_input['max_concurrent_transforms'],
            'MaxPayloadInMB': execution_input['max_payload'],
        }

    step = TransformStep('Inference',
        transformer=pca_transformer,
        data=execution_input['data'],
        data_type=execution_input['data_type'],
        content_type=execution_input['content_type'],
        compression_type=execution_input['compression_type'],
        split_type=execution_input['split_type'],
        job_name=execution_input['job_name'],
        model_name=execution_input['model_name'],
        experiment_config={
            'ExperimentName': 'pca_experiment',
            'TrialName': 'pca_trial',
            'TrialComponentDisplayName': 'Transform'
        },
        tags=execution_input['tags'],
        join_source=execution_input['join_source'],
        output_filter=execution_input['output_filter'],
        input_filter=execution_input['input_filter'],
        parameters=parameters
    )

    assert step.to_dict()['Parameters'] == {
        'BatchStrategy.$': "$$.Execution.Input['strategy']",
        'ModelName.$': "$$.Execution.Input['model_name']",
        'TransformInput': {
            'CompressionType.$': "$$.Execution.Input['compression_type']",
            'ContentType.$': "$$.Execution.Input['content_type']",
            'DataSource': {
                'S3DataSource': {
                    'S3DataType.$': "$$.Execution.Input['data_type']",
                    'S3Uri.$': "$$.Execution.Input['data']"
                }
            },
            'SplitType.$': "$$.Execution.Input['split_type']"
        },
        'TransformOutput': {
            'Accept.$': "$$.Execution.Input['accept']",
            'AssembleWith.$': "$$.Execution.Input['assemble_with']",
            'KmsKeyId.$': "$$.Execution.Input['output_kms_key']",
            'S3OutputPath.$': "$$.Execution.Input['output_path']"
        },
        'TransformJobName.$': "$$.Execution.Input['job_name']",
        'TransformResources': {
            'InstanceCount.$': "$$.Execution.Input['instance_count']",
            'InstanceType.$': "$['instance_type']",
            'VolumeKmsKeyId.$': "$$.Execution.Input['volume_kms_key']"
        },
        'ExperimentConfig.$': "$$.Execution.Input['experiment_config']",
        'DataProcessing': {
            'InputFilter.$': "$$.Execution.Input['input_filter']",
            'OutputFilter.$': "$$.Execution.Input['output_filter']",
            'JoinSource.$': "$$.Execution.Input['join_source']",
        },
        'Tags.$': "$$.Execution.Input['tags']",
        'Environment.$': "$$.Execution.Input['env']",
        'MaxConcurrentTransforms.$': "$$.Execution.Input['max_concurrent_transforms']",
        'MaxPayloadInMB.$': "$$.Execution.Input['max_payload']"
    }


@patch('botocore.client.BaseClient._make_api_call', new=mock_boto_api_call)
@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_get_expected_model(pca_estimator):
    training_step = TrainingStep('Training', estimator=pca_estimator, job_name='TrainingJob')
    expected_model = training_step.get_expected_model()
    model_step = ModelStep('Create model', model=expected_model, model_name='pca-model')
    assert model_step.to_dict() == {
        'Type': 'Task',
        'Parameters': {
            'ExecutionRoleArn': EXECUTION_ROLE,
            'ModelName': 'pca-model',
            'PrimaryContainer': {
                'Environment': {},
                'Image': expected_model.image_uri,
                'ModelDataUrl.$': "$['ModelArtifacts']['S3ModelArtifacts']"
            }
        },
        'Resource': 'arn:aws:states:::sagemaker:createModel',
        'End': True
    }


@patch('botocore.client.BaseClient._make_api_call', new=mock_boto_api_call)
@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_get_expected_model_with_env(pca_estimator_with_env):
    training_step = TrainingStep('Training', estimator=pca_estimator_with_env, job_name='TrainingJob')
    expected_model = training_step.get_expected_model()
    model_step = ModelStep('Create model', model=expected_model, model_name='pca-model')
    assert model_step.to_dict() == {
        'Type': 'Task',
        'Parameters': {
            'ExecutionRoleArn': EXECUTION_ROLE,
            'ModelName': 'pca-model',
            'PrimaryContainer': {
                'Environment': {
                    'JobName': 'job_name',
                    'ModelName': 'model_name'
                },
                'Image': expected_model.image_uri,
                'ModelDataUrl.$': "$['ModelArtifacts']['S3ModelArtifacts']"
            }
        },
        'Resource': 'arn:aws:states:::sagemaker:createModel',
        'End': True
    }


@patch('botocore.client.BaseClient._make_api_call', new=mock_boto_api_call)
@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_get_expected_model_with_framework_estimator(tensorflow_estimator):
    training_step = TrainingStep('Training',
        estimator=tensorflow_estimator,
        data={'train': 's3://sagemaker/train'},
        job_name='tensorflow-job',
        mini_batch_size=1024
    )
    expected_model = training_step.get_expected_model()
    expected_model.entry_point = 'tf_train.py'
    model_step = ModelStep('Create model', model=expected_model, model_name='tf-model')
    assert model_step.to_dict() == {
        'Type': 'Task',
        'Parameters': {
            'ExecutionRoleArn': EXECUTION_ROLE,
            'ModelName': 'tf-model',
            'PrimaryContainer': {
                'Environment': {
                    'SAGEMAKER_PROGRAM': 'tf_train.py',
                    'SAGEMAKER_SUBMIT_DIRECTORY': 's3://sagemaker/tensorflow-job/source/sourcedir.tar.gz',
                    'SAGEMAKER_CONTAINER_LOG_LEVEL': '20',
                    'SAGEMAKER_REGION': 'us-east-1',
                },
                'Image': expected_model.image_uri,
                'ModelDataUrl.$': "$['ModelArtifacts']['S3ModelArtifacts']"
            }
        },
        'Resource': 'arn:aws:states:::sagemaker:createModel',
        'End': True
    }


@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_model_step_creation(pca_model):
    step = ModelStep('Create model', model=pca_model, model_name='pca-model', tags=DEFAULT_TAGS)
    assert step.to_dict() == {
        'Type': 'Task',
        'Parameters': {
            'ExecutionRoleArn': EXECUTION_ROLE,
            'ModelName': 'pca-model',
            'PrimaryContainer': {
                'Environment': {},
                'Image': pca_model.image_uri,
                'ModelDataUrl': pca_model.model_data
            },
            'Tags': DEFAULT_TAGS_LIST
        },
        'Resource': 'arn:aws:states:::sagemaker:createModel',
        'End': True
    }


@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_model_step_creation_with_placeholders(pca_model):
    execution_input = ExecutionInput(schema={
        'Environment': str,
        'Tags': str
    })

    step_input = StepInput(schema={
        'ModelName': str
    })

    parameters = {
        'PrimaryContainer': {
            'Environment': execution_input['Environment']
        }
    }
    step = ModelStep('Create model', model=pca_model, model_name=step_input['ModelName'], tags=execution_input['Tags'],
                     parameters=parameters)
    assert step.to_dict()['Parameters'] == {
        'ExecutionRoleArn': EXECUTION_ROLE,
        'ModelName.$': "$['ModelName']",
        'PrimaryContainer': {
            'Environment.$': "$$.Execution.Input['Environment']",
            'Image': pca_model.image_uri,
            'ModelDataUrl': pca_model.model_data
        },
        'Tags.$': "$$.Execution.Input['Tags']"
    }


@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_model_step_creation_with_env(pca_model_with_env):
    step = ModelStep('Create model', model=pca_model_with_env, model_name='pca-model', tags=DEFAULT_TAGS)
    assert step.to_dict() == {
        'Type': 'Task',
        'Parameters': {
            'ExecutionRoleArn': EXECUTION_ROLE,
            'ModelName': 'pca-model',
            'PrimaryContainer': {
                'Environment': {
                    'JobName': 'job_name',
                    'ModelName': 'model_name'
                },
                'Image': pca_model_with_env.image_uri,
                'ModelDataUrl': pca_model_with_env.model_data
            },
            'Tags': DEFAULT_TAGS_LIST
        },
        'Resource': 'arn:aws:states:::sagemaker:createModel',
        'End': True
    }


@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_endpoint_config_step_creation(pca_model):
    data_capture_config = DataCaptureConfig(
        enable_capture=True,
        sampling_percentage=100,
        destination_s3_uri='s3://sagemaker/datacapture')
    step = EndpointConfigStep('Endpoint Config',
        endpoint_config_name='MyEndpointConfig',
        model_name='pca-model',
        initial_instance_count=1,
        instance_type='ml.p2.xlarge',
        data_capture_config=data_capture_config,
        tags=DEFAULT_TAGS,
        )
    assert step.to_dict() == {
        'Type': 'Task',
        'Parameters': {
            'EndpointConfigName': 'MyEndpointConfig',
            'ProductionVariants': [{
                'InitialInstanceCount': 1,
                'InstanceType': 'ml.p2.xlarge',
                'ModelName': 'pca-model',
                'VariantName': 'AllTraffic'
            }],
            'DataCaptureConfig': {
                'EnableCapture': True,
                'InitialSamplingPercentage': 100,
                'DestinationS3Uri': 's3://sagemaker/datacapture',
                'CaptureOptions': [
                    {'CaptureMode': 'Input'},
                    {'CaptureMode': 'Output'}
                ],
                'CaptureContentTypeHeader': {
                    'CsvContentTypes': ['text/csv'],
                    'JsonContentTypes': ['application/json']
                }
            },
            'Tags': DEFAULT_TAGS_LIST
        },
        'Resource': 'arn:aws:states:::sagemaker:createEndpointConfig',
        'End': True
    }


@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_endpoint_step_creation(pca_model):
    step = EndpointStep('Endpoint', endpoint_name='MyEndPoint', endpoint_config_name='MyEndpointConfig', tags=DEFAULT_TAGS)
    assert step.to_dict() == {
        'Type': 'Task',
        'Parameters': {
            'EndpointConfigName': 'MyEndpointConfig',
            'EndpointName': 'MyEndPoint',
            'Tags': DEFAULT_TAGS_LIST
        },
        'Resource': 'arn:aws:states:::sagemaker:createEndpoint',
        'End': True
    }

    step = EndpointStep('Endpoint', endpoint_name='MyEndPoint', endpoint_config_name='MyEndpointConfig', update=True, tags=DEFAULT_TAGS)
    assert step.to_dict() == {
        'Type': 'Task',
        'Parameters': {
            'EndpointConfigName': 'MyEndpointConfig',
            'EndpointName': 'MyEndPoint',
            'Tags': DEFAULT_TAGS_LIST
        },
        'Resource': 'arn:aws:states:::sagemaker:updateEndpoint',
        'End': True
    }


@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_processing_step_creation(sklearn_processor):
    inputs = [ProcessingInput(source='dataset.csv', destination='/opt/ml/processing/input')]
    outputs = [
        ProcessingOutput(source='/opt/ml/processing/output/train'),
        ProcessingOutput(source='/opt/ml/processing/output/validation'),
        ProcessingOutput(source='/opt/ml/processing/output/test')
    ]
    step = ProcessingStep('Feature Transformation', sklearn_processor, 'MyProcessingJob', inputs=inputs, outputs=outputs)
    assert step.to_dict() == {
        'Type': 'Task',
        'Parameters': {
            'AppSpecification': {
                'ImageUri': '683313688378.dkr.ecr.us-east-1.amazonaws.com/sagemaker-scikit-learn:0.20.0-cpu-py3'
            },
            'ProcessingInputs': [
                {
                    'InputName': None,
                    'AppManaged': False,
                    'S3Input': {
                        'LocalPath': '/opt/ml/processing/input',
                        'S3CompressionType': 'None',
                        'S3DataDistributionType': 'FullyReplicated',
                        'S3DataType': 'S3Prefix',
                        'S3InputMode': 'File',
                        'S3Uri': 'dataset.csv'
                    }
                }
            ],
            'ProcessingOutputConfig': {
                'Outputs': [
                    {
                        'OutputName': None,
                        'AppManaged': False,
                        'S3Output': {
                            'LocalPath': '/opt/ml/processing/output/train',
                            'S3UploadMode': 'EndOfJob',
                            'S3Uri': None
                        }
                    },
                    {
                        'OutputName': None,
                        'AppManaged': False,
                        'S3Output': {
                            'LocalPath': '/opt/ml/processing/output/validation',
                            'S3UploadMode': 'EndOfJob',
                            'S3Uri': None
                        }
                    },
                    {
                        'OutputName': None,
                        'AppManaged': False,
                        'S3Output': {
                            'LocalPath': '/opt/ml/processing/output/test',
                            'S3UploadMode': 'EndOfJob',
                            'S3Uri': None
                        }
                    }
                ]
            },
            'ProcessingResources': {
                'ClusterConfig': {
                    'InstanceCount': 1,
                    'InstanceType': 'ml.m5.xlarge',
                    'VolumeSizeInGB': 30
                }
            },
            'ProcessingJobName': 'MyProcessingJob',
            'RoleArn': EXECUTION_ROLE
        },
        'Resource': 'arn:aws:states:::sagemaker:createProcessingJob.sync',
        'End': True
    }


def test_processing_step_creation_with_placeholders(sklearn_processor):
    execution_input = ExecutionInput(schema={
        'image_uri': str,
        'instance_count': int,
        'entrypoint': str,
        'output_kms_key': str,
        'role': str,
        'env': str,
        'volume_size_in_gb': int,
        'volume_kms_key': str,
        'max_runtime_in_seconds': int,
        'tags': [{str: str}],
        'container_arguments': [str]
    })

    step_input = StepInput(schema={
        'instance_type': str
    })

    parameters = {
        'AppSpecification': {
            'ContainerEntrypoint': execution_input['entrypoint'],
            'ImageUri': execution_input['image_uri']
        },
        'Environment': execution_input['env'],
        'ProcessingOutputConfig': {
            'KmsKeyId': execution_input['output_kms_key']
        },
        'ProcessingResources': {
            'ClusterConfig': {
                'InstanceCount': execution_input['instance_count'],
                'InstanceType': step_input['instance_type'],
                'VolumeKmsKeyId': execution_input['volume_kms_key'],
                'VolumeSizeInGB': execution_input['volume_size_in_gb']
            }
        },
        'RoleArn': execution_input['role'],
        'StoppingCondition': {
            'MaxRuntimeInSeconds': execution_input['max_runtime_in_seconds']
        },
        'Tags': execution_input['tags']
    }

    inputs = [ProcessingInput(source='dataset.csv', destination='/opt/ml/processing/input')]
    outputs = [
        ProcessingOutput(source='/opt/ml/processing/output/train'),
        ProcessingOutput(source='/opt/ml/processing/output/validation'),
        ProcessingOutput(source='/opt/ml/processing/output/test')
    ]
    step = ProcessingStep(
        'Feature Transformation',
        sklearn_processor,
        'MyProcessingJob',
        container_entrypoint=execution_input['entrypoint'],
        container_arguments=execution_input['container_arguments'],
        kms_key_id=execution_input['output_kms_key'],
        inputs=inputs,
        outputs=outputs,
        parameters=parameters
    )
    assert step.to_dict() == {
        'Type': 'Task',
        'Parameters': {
            'AppSpecification': {
                'ContainerArguments.$': "$$.Execution.Input['container_arguments']",
                'ContainerEntrypoint.$': "$$.Execution.Input['entrypoint']",
                'ImageUri.$': "$$.Execution.Input['image_uri']"
            },
            'Environment.$': "$$.Execution.Input['env']",
            'ProcessingInputs': [
                {
                    'InputName': None,
                    'AppManaged': False,
                    'S3Input': {
                        'LocalPath': '/opt/ml/processing/input',
                        'S3CompressionType': 'None',
                        'S3DataDistributionType': 'FullyReplicated',
                        'S3DataType': 'S3Prefix',
                        'S3InputMode': 'File',
                        'S3Uri': 'dataset.csv'
                    }
                }
            ],
            'ProcessingOutputConfig': {
                'KmsKeyId.$': "$$.Execution.Input['output_kms_key']",
                'Outputs': [
                    {
                        'OutputName': None,
                        'AppManaged': False,
                        'S3Output': {
                            'LocalPath': '/opt/ml/processing/output/train',
                            'S3UploadMode': 'EndOfJob',
                            'S3Uri': None
                        }
                    },
                    {
                        'OutputName': None,
                        'AppManaged': False,
                        'S3Output': {
                            'LocalPath': '/opt/ml/processing/output/validation',
                            'S3UploadMode': 'EndOfJob',
                            'S3Uri': None
                        }
                    },
                    {
                        'OutputName': None,
                        'AppManaged': False,
                        'S3Output': {
                            'LocalPath': '/opt/ml/processing/output/test',
                            'S3UploadMode': 'EndOfJob',
                            'S3Uri': None
                        }
                    }
                ]
            },
            'ProcessingResources': {
                'ClusterConfig': {
                    'InstanceCount.$': "$$.Execution.Input['instance_count']",
                    'InstanceType.$': "$['instance_type']",
                    'VolumeKmsKeyId.$': "$$.Execution.Input['volume_kms_key']",
                    'VolumeSizeInGB.$': "$$.Execution.Input['volume_size_in_gb']"
                }
            },
            'ProcessingJobName': 'MyProcessingJob',
            'RoleArn.$': "$$.Execution.Input['role']",
            'Tags.$': "$$.Execution.Input['tags']",
            'StoppingCondition': {'MaxRuntimeInSeconds.$': "$$.Execution.Input['max_runtime_in_seconds']"},
        },
        'Resource': 'arn:aws:states:::sagemaker:createProcessingJob.sync',
        'End': True
    }
