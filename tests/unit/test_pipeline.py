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

from sagemaker.sklearn.estimator import SKLearn
from unittest.mock import MagicMock, patch
from stepfunctions.template import TrainingPipeline, InferencePipeline
from sagemaker.debugger import DebuggerHookConfig

from tests.unit.utils import mock_boto_api_call

SAGEMAKER_EXECUTION_ROLE = 'SageMakerExecutionRole'
STEPFUNCTIONS_EXECUTION_ROLE = 'StepFunctionsExecutionRole'
PCA_IMAGE = '382416733822.dkr.ecr.us-east-1.amazonaws.com/pca:1'
LINEAR_LEARNER_IMAGE = '382416733822.dkr.ecr.us-east-1.amazonaws.com/linear-learner:1'


@pytest.fixture
def pca_estimator():
    s3_output_location = 's3://sagemaker/models'
    sagemaker_session = MagicMock()
    sagemaker_session.boto_region_name = 'us-east-1'

    pca = sagemaker.estimator.Estimator(
        PCA_IMAGE,
        role=SAGEMAKER_EXECUTION_ROLE,
        instance_count=1,
        instance_type='ml.c4.xlarge',
        output_path=s3_output_location,
        sagemaker_session=sagemaker_session
    )

    pca.set_hyperparameters(
        feature_dim=50000,
        num_components=10,
        subtract_mean=True,
        algorithm_mode='randomized',
        mini_batch_size=200
    )

    return pca


@pytest.fixture
def sklearn_preprocessor():
    script_path = 'sklearn_abalone_featurizer.py'
    source_dir = 's3://sagemaker/source'
    sagemaker_session = MagicMock()
    sagemaker_session.boto_region_name = 'us-east-1'

    sklearn_preprocessor = SKLearn(
        framework_version='0.20.0',
        py_version='py3',
        entry_point=script_path,
        role=SAGEMAKER_EXECUTION_ROLE,
        instance_type="ml.c4.xlarge",
        source_dir=source_dir,
        sagemaker_session = sagemaker_session
    )

    sklearn_preprocessor.debugger_hook_config = DebuggerHookConfig(
        s3_output_path='s3://sagemaker/source/debug'
    )
    
    return sklearn_preprocessor


@pytest.fixture
def linear_learner_estimator():
    s3_output_location = 's3://sagemaker/models'
    sagemaker_session = MagicMock()
    sagemaker_session.boto_region_name = 'us-east-1'

    ll_estimator = sagemaker.estimator.Estimator(
        LINEAR_LEARNER_IMAGE,
        SAGEMAKER_EXECUTION_ROLE, 
        instance_count=1, 
        instance_type='ml.c4.xlarge',
        volume_size=20,
        max_run=3600,
        input_mode='File',
        output_path=s3_output_location,
        sagemaker_session=sagemaker_session
    )

    ll_estimator.debugger_hook_config = DebuggerHookConfig(
        s3_output_path='s3://sagemaker/models/debug'
    )

    ll_estimator.set_hyperparameters(feature_dim=10, predictor_type='regressor', mini_batch_size=32)

    return ll_estimator


@patch('botocore.client.BaseClient._make_api_call', new=mock_boto_api_call)
@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_pca_training_pipeline(pca_estimator):
    s3_inputs = {
        'train': 's3://sagemaker/pca/train'
    }
    s3_bucket = 'sagemaker-us-east-1'

    pipeline = TrainingPipeline(pca_estimator, STEPFUNCTIONS_EXECUTION_ROLE, s3_inputs, s3_bucket)
    result = pipeline.workflow.definition.to_dict()
    assert result['StartAt'] == 'Training'
    assert len(result['States']) == 4
    assert result['States']['Training'] == {
        'Parameters': {
            'AlgorithmSpecification.$': "$$.Execution.Input['Training'].AlgorithmSpecification",
            'HyperParameters.$': "$$.Execution.Input['Training'].HyperParameters",
            'InputDataConfig.$': "$$.Execution.Input['Training'].InputDataConfig",
            'OutputDataConfig.$': "$$.Execution.Input['Training'].OutputDataConfig",
            'ResourceConfig.$': "$$.Execution.Input['Training'].ResourceConfig",
            'RoleArn.$': "$$.Execution.Input['Training'].RoleArn",
            'StoppingCondition.$': "$$.Execution.Input['Training'].StoppingCondition",
            'TrainingJobName.$': "$$.Execution.Input['Training'].TrainingJobName"
        },
        'Resource': 'arn:aws:states:::sagemaker:createTrainingJob.sync',
        'Type': 'Task',
        'Next': 'Create Model'
    }
    
    assert result['States']['Create Model'] == {
        'Type': 'Task',
        'Parameters': {
            'ExecutionRoleArn.$': "$$.Execution.Input['Create Model'].ExecutionRoleArn",
            'ModelName.$': "$$.Execution.Input['Create Model'].ModelName",
            'PrimaryContainer.$': "$$.Execution.Input['Create Model'].PrimaryContainer"
        },
        'Resource': 'arn:aws:states:::sagemaker:createModel',
        'Next': 'Configure Endpoint'
    }

    assert result['States']['Configure Endpoint'] == {
        'Resource': 'arn:aws:states:::sagemaker:createEndpointConfig',
        'Parameters': {
            'EndpointConfigName.$': "$$.Execution.Input['Configure Endpoint'].EndpointConfigName",
            'ProductionVariants.$': "$$.Execution.Input['Configure Endpoint'].ProductionVariants"
        },
        'Type': 'Task',
        'Next': 'Deploy'
    }

    assert result['States']['Deploy'] == {
        'Resource': 'arn:aws:states:::sagemaker:createEndpoint',
        'Parameters': {
            'EndpointName.$': "$$.Execution.Input['Deploy'].EndpointName",
            'EndpointConfigName.$': "$$.Execution.Input['Deploy'].EndpointConfigName"
        },
        'Type': 'Task',
        'End': True
    }

    workflow = MagicMock()
    workflow_name = workflow.name = 'training-pipeline'
    pipeline.workflow = workflow

    job_name = 'pca'
    execution = pipeline.execute(job_name=job_name)
    inputs = {
        'Training': {
            'AlgorithmSpecification': {
                'TrainingImage': '382416733822.dkr.ecr.us-east-1.amazonaws.com/pca:1', 
                'TrainingInputMode': 'File'
            },
            'OutputDataConfig': {
                'S3OutputPath': 's3://sagemaker-us-east-1/' + workflow_name + '/models'
            },
            'StoppingCondition': {
                'MaxRuntimeInSeconds': 86400
            },
            'ResourceConfig': {
                'InstanceCount': 1,
                'InstanceType': 'ml.c4.xlarge',
                'VolumeSizeInGB': 30
            },
            'RoleArn': 'SageMakerExecutionRole', 
            'InputDataConfig': [{
                'DataSource': {
                    'S3DataSource': {
                        'S3DataDistributionType': 'FullyReplicated',
                        'S3DataType': 'S3Prefix',
                        'S3Uri': 's3://sagemaker/pca/train'
                    }
                },
                'ChannelName': 'train'
            }],
            'HyperParameters': {
                'feature_dim': '50000',
                'num_components': '10',
                'subtract_mean': 'True',
                'algorithm_mode': 'randomized',
                'mini_batch_size': '200'
            },
            'TrainingJobName': 'estimator-'+job_name
        },
        'Create Model': {
            'ModelName': job_name,
            'PrimaryContainer': {
                'Image': '382416733822.dkr.ecr.us-east-1.amazonaws.com/pca:1',
                'Environment': {},
                'ModelDataUrl': 's3://sagemaker-us-east-1/' + workflow_name + '/models/' + 'estimator-'+job_name + '/output/model.tar.gz'
            },
            'ExecutionRoleArn': 'SageMakerExecutionRole'
        },
        'Configure Endpoint': {
            'EndpointConfigName': job_name, 
            'ProductionVariants': [{
                'ModelName': job_name,
                'InstanceType': 'ml.c4.xlarge',
                'InitialInstanceCount': 1,
                'VariantName': 'AllTraffic'
            }]
        },
        'Deploy': {
            'EndpointName': job_name,
            'EndpointConfigName': job_name
        }
    }

    workflow.execute.assert_called_with(name=job_name, inputs=inputs)


@patch('botocore.client.BaseClient._make_api_call', new=mock_boto_api_call)
@patch.object(boto3.session.Session, 'region_name', 'us-east-1')
def test_inference_pipeline(sklearn_preprocessor, linear_learner_estimator):
    s3_inputs = {
        'train': 's3://sagemaker-us-east-1/inference/train'
    }
    s3_bucket = 'sagemaker-us-east-1'

    pipeline = InferencePipeline(
        preprocessor=sklearn_preprocessor,
        estimator=linear_learner_estimator,
        inputs=s3_inputs,
        s3_bucket=s3_bucket,
        role=STEPFUNCTIONS_EXECUTION_ROLE
    )
    result = pipeline.get_workflow().definition.to_dict()
    assert result['StartAt'] == 'Train Preprocessor'
    assert len(result['States']) == 7

    assert result['States']['Train Preprocessor'] == {
        'Parameters': {
            'AlgorithmSpecification.$': "$$.Execution.Input['Train Preprocessor'].AlgorithmSpecification",
            'DebugHookConfig.$': "$$.Execution.Input['Train Preprocessor'].DebugHookConfig",
            'HyperParameters.$': "$$.Execution.Input['Train Preprocessor'].HyperParameters",
            'InputDataConfig.$': "$$.Execution.Input['Train Preprocessor'].InputDataConfig",
            'OutputDataConfig.$': "$$.Execution.Input['Train Preprocessor'].OutputDataConfig",
            'ResourceConfig.$': "$$.Execution.Input['Train Preprocessor'].ResourceConfig",
            'RoleArn.$': "$$.Execution.Input['Train Preprocessor'].RoleArn",
            'StoppingCondition.$': "$$.Execution.Input['Train Preprocessor'].StoppingCondition",
            'TrainingJobName.$': "$$.Execution.Input['Train Preprocessor'].TrainingJobName"
        },
        'Resource': 'arn:aws:states:::sagemaker:createTrainingJob.sync',
        'Type': 'Task',
        'Next': 'Create Preprocessor Model'
    }

    assert result['States']['Create Preprocessor Model'] == {
        'Type': 'Task',
        'Parameters': {
            'ExecutionRoleArn.$': "$$.Execution.Input['Create Preprocessor Model'].ExecutionRoleArn",
            'ModelName.$': "$$.Execution.Input['Create Preprocessor Model'].ModelName",
            'PrimaryContainer.$': "$$.Execution.Input['Create Preprocessor Model'].PrimaryContainer"
        },
        'Resource': 'arn:aws:states:::sagemaker:createModel',
        'Next': 'Transform Input'
    }

    assert result['States']['Transform Input'] == {
        'Type': 'Task',
        'Parameters': {
            'Environment.$': "$$.Execution.Input['Transform Input'].Environment",
            'ModelName.$': "$$.Execution.Input['Transform Input'].ModelName",
            'TransformInput.$': "$$.Execution.Input['Transform Input'].TransformInput",
            'TransformJobName.$': "$$.Execution.Input['Transform Input'].TransformJobName",
            'TransformOutput.$': "$$.Execution.Input['Transform Input'].TransformOutput",
            'TransformResources.$': "$$.Execution.Input['Transform Input'].TransformResources",
            'MaxPayloadInMB.$': "$$.Execution.Input['Transform Input'].MaxPayloadInMB",
        },
        'Resource': 'arn:aws:states:::sagemaker:createTransformJob.sync',
        'Next': 'Training'
    }

    assert result['States']['Create Pipeline Model'] == {
        'Type': 'Task',
        'Parameters': {
            'ExecutionRoleArn.$': "$$.Execution.Input['Create Pipeline Model'].ExecutionRoleArn",
            'ModelName.$': "$$.Execution.Input['Create Pipeline Model'].ModelName",
            'Containers.$': "$$.Execution.Input['Create Pipeline Model'].Containers"
        },
        'Resource': 'arn:aws:states:::sagemaker:createModel',
        'Next': 'Configure Endpoint'
    }

    assert result['States']['Configure Endpoint'] == {
        'Resource': 'arn:aws:states:::sagemaker:createEndpointConfig',
        'Parameters': {
            'EndpointConfigName.$': "$$.Execution.Input['Configure Endpoint'].EndpointConfigName",
            'ProductionVariants.$': "$$.Execution.Input['Configure Endpoint'].ProductionVariants"
        },
        'Type': 'Task',
        'Next': 'Deploy'
    }

    assert result['States']['Deploy'] == {
        'Resource': 'arn:aws:states:::sagemaker:createEndpoint',
        'Parameters': {
            'EndpointName.$': "$$.Execution.Input['Deploy'].EndpointName",
            'EndpointConfigName.$': "$$.Execution.Input['Deploy'].EndpointConfigName"
        },
        'Type': 'Task',
        'End': True
    }

    workflow = MagicMock()
    workflow_name = workflow.name = 'inference-pipeline'
    pipeline.workflow = workflow

    job_name = 'linear_learner'
    execution = pipeline.execute(job_name=job_name)

    inputs = {
        'Train Preprocessor': {
            'AlgorithmSpecification': {
                'TrainingImage': '683313688378.dkr.ecr.us-east-1.amazonaws.com/sagemaker-scikit-learn:0.20.0-cpu-py3',
                'TrainingInputMode': 'File'
            },
            'HyperParameters': {
                'sagemaker_container_log_level': '20',
                'sagemaker_job_name': '"preprocessor-linear_learner"',
                'sagemaker_program': '"sklearn_abalone_featurizer.py"',
                'sagemaker_region': '"us-east-1"',
                'sagemaker_submit_directory': '"s3://sagemaker/source"',
            },
            'InputDataConfig': [{
                'ChannelName': 'train',
                'DataSource': {
                    'S3DataSource': {
                        'S3DataDistributionType': 'FullyReplicated',
                        'S3DataType': 'S3Prefix',
                        'S3Uri': 's3://sagemaker-us-east-1/inference/train'
                    }
                }
            }],
            'OutputDataConfig': {
                'S3OutputPath': 's3://sagemaker-us-east-1/inference-pipeline/models'
            },
            'DebugHookConfig': {
                'S3OutputPath': 's3://sagemaker-us-east-1/inference-pipeline/models/debug'
            },
            'ResourceConfig': {
                'InstanceCount': 1,
                'InstanceType': 'ml.c4.xlarge',
                'VolumeSizeInGB': 30
            },
            'RoleArn': 'SageMakerExecutionRole',
            'StoppingCondition': { 'MaxRuntimeInSeconds': 86400 },
            'TrainingJobName': 'preprocessor-linear_learner'
        },
        'Create Preprocessor Model': {
            'ExecutionRoleArn': 'SageMakerExecutionRole',
            'ModelName': 'preprocessor-linear_learner',
            'PrimaryContainer': {
                'Environment': {
                    'SAGEMAKER_CONTAINER_LOG_LEVEL': '20',
                    'SAGEMAKER_PROGRAM': 'sklearn_abalone_featurizer.py',
                    'SAGEMAKER_REGION': 'us-east-1',
                    'SAGEMAKER_SUBMIT_DIRECTORY': 's3://sagemaker/source'
                },
                'Image': '683313688378.dkr.ecr.us-east-1.amazonaws.com/sagemaker-scikit-learn:0.20.0-cpu-py3',
                'ModelDataUrl': 's3://sagemaker-us-east-1/inference-pipeline/models/preprocessor-linear_learner/output/model.tar.gz'
            }
        },
        'Transform Input': {
            'Environment': {},
            'ModelName': 'preprocessor-linear_learner',
            'TransformInput': {
                'DataSource': {
                    'S3DataSource': {
                        'S3DataType': 'S3Prefix',
                        'S3Uri': 's3://sagemaker-us-east-1/inference/train'
                    }
                }
            },
            'TransformJobName': 'preprocessor-linear_learner',
            'TransformOutput': { 'S3OutputPath': 's3://sagemaker-us-east-1/inference-pipeline/preprocessor-transform-linear_learner/transform' },
            'TransformResources': {
                'InstanceCount': 1,
                'InstanceType': 'ml.c4.xlarge'
            },
            'MaxPayloadInMB': 20
        },
        'Training': {
            'AlgorithmSpecification': {
                'TrainingImage': '382416733822.dkr.ecr.us-east-1.amazonaws.com/linear-learner:1',
                'TrainingInputMode': 'File'
            },
            'HyperParameters': {
                'feature_dim': '10',
                'mini_batch_size': '32',
                'predictor_type': 'regressor'
            },
            'InputDataConfig': [{
                'ChannelName': 'train',
                'DataSource': {
                    'S3DataSource': {
                        'S3DataDistributionType': 'FullyReplicated',
                        'S3DataType': 'S3Prefix',
                        'S3Uri': 's3://sagemaker-us-east-1/inference-pipeline/preprocessor-transform-linear_learner/transform'
                    }
                }
            }],
            'OutputDataConfig': { 'S3OutputPath': 's3://sagemaker-us-east-1/inference-pipeline/models' },
            'DebugHookConfig': { 'S3OutputPath': 's3://sagemaker-us-east-1/inference-pipeline/models/debug' },
            'ResourceConfig': {
                'InstanceCount': 1,
                'InstanceType': 'ml.c4.xlarge',
                'VolumeSizeInGB': 20
            },
            'RoleArn': 'SageMakerExecutionRole',
            'StoppingCondition': { 'MaxRuntimeInSeconds': 3600 },
            'TrainingJobName': 'estimator-linear_learner'
        },
        'Create Pipeline Model': {
            'Containers': [
                {
                    'Environment': {
                        'SAGEMAKER_CONTAINER_LOG_LEVEL': '20',
                        'SAGEMAKER_PROGRAM': 'sklearn_abalone_featurizer.py',
                        'SAGEMAKER_REGION': 'us-east-1',
                        'SAGEMAKER_SUBMIT_DIRECTORY': 's3://sagemaker/source'
                    },
                    'Image': '683313688378.dkr.ecr.us-east-1.amazonaws.com/sagemaker-scikit-learn:0.20.0-cpu-py3',
                    'ModelDataUrl': 's3://sagemaker-us-east-1/inference-pipeline/models/preprocessor-linear_learner/output/model.tar.gz'
                },
                {
                    'Environment': {},
                    'Image': '382416733822.dkr.ecr.us-east-1.amazonaws.com/linear-learner:1',
                    'ModelDataUrl': 's3://sagemaker-us-east-1/inference-pipeline/models/estimator-linear_learner/output/model.tar.gz'
                }
            ],
            'ExecutionRoleArn': 'SageMakerExecutionRole',
            'ModelName': 'linear_learner'
        },
        'Configure Endpoint': {
            'EndpointConfigName': 'linear_learner',
            'ProductionVariants': [{
                'InitialInstanceCount': 1,
                'InstanceType': 'ml.c4.xlarge',
                'ModelName': 'linear_learner',
                'VariantName': 'AllTraffic'
            }]
        },
        'Deploy': {
            'EndpointConfigName': 'linear_learner',
            'EndpointName': 'linear_learner'
        }
    }
    
    workflow.execute.assert_called_with(name=job_name, inputs=inputs)
