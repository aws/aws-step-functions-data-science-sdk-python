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
import json

from sagemaker.utils import unique_name_from_base
from sagemaker.image_uris import retrieve
from stepfunctions import steps
from stepfunctions.workflow import Workflow
from stepfunctions.steps.utils import get_aws_partition
from tests.integ.utils import state_machine_delete_wait


@pytest.fixture(scope="module")
def training_job_parameters(sagemaker_session, sagemaker_role_arn, record_set_fixture):
    parameters = {
        "AlgorithmSpecification": {
            "TrainingImage": retrieve(region=sagemaker_session.boto_session.region_name, framework='pca'),
            "TrainingInputMode": "File"
        },
        "OutputDataConfig": {
            "S3OutputPath": "s3://{}/".format(sagemaker_session.default_bucket())
        },
        "StoppingCondition": {
            "MaxRuntimeInSeconds": 86400
        },
        "ResourceConfig": {
            "InstanceCount": 1,
            "InstanceType": "ml.m5.large",
            "VolumeSizeInGB": 30
        },
        "RoleArn": sagemaker_role_arn,
        "InputDataConfig":[
        {
            "DataSource": {
                "S3DataSource": {
                    "S3DataDistributionType": "ShardedByS3Key",
                    "S3DataType": "ManifestFile",
                    "S3Uri": record_set_fixture.s3_data
                }
            },
            "ChannelName": "train"
        }
        ],
        "HyperParameters": {
            "num_components": "48",
            "feature_dim": "784",
            "mini_batch_size": "200"
        },
        "TrainingJobName": unique_name_from_base("integ-test-task-workflow")
    }

    return parameters


def workflow_test_suite(sfn_client, workflow, asl_state_machine_definition, output_result, inputs=None):
    state_machine_arn = workflow.create()
    execution = workflow.execute(inputs=inputs)
    response = sfn_client.describe_state_machine(stateMachineArn=execution.workflow.state_machine_arn)
    assert asl_state_machine_definition == json.loads(response.get('definition'))

    execution_output = execution.get_output(wait=True)
    assert execution_output == output_result

    state_machine_delete_wait(sfn_client, workflow.state_machine_arn)


def test_pass_state_machine_creation(sfn_client, sfn_role_arn):
    pass_state_name = "Pass"
    pass_state_result = "Pass Result"
    asl_state_machine_definition = {
        "StartAt": pass_state_name,
        "States": {
            pass_state_name: {
                "Result": pass_state_result,
                "Type": "Pass",
                "End": True
            }
        }
    }

    definition = steps.Pass(pass_state_name, result=pass_state_result)
    workflow = Workflow(
        unique_name_from_base('Test_Pass_Workflow'),
        definition=definition,
        role=sfn_role_arn
    )

    workflow_test_suite(sfn_client, workflow, asl_state_machine_definition, pass_state_result)


def test_wait_state_machine_creation(sfn_client, sfn_role_arn):
    first_state_name = "FirstState"
    first_wait_state_name = "WaitInSeconds"
    second_wait_state_name = "WaitTimestamp"
    third_wait_state_name = "WaitTimestampPath"
    fourth_wait_state_name = "WaitInSecondsPath"
    final_state_name = "FinalState"
    timestamp = "2019-09-04T01:59:00Z"
    timestamp_path = "$.expirydate"
    seconds = 2
    seconds_path = "$.expiryseconds"
    wait_state_result = "Wait Result"
    parameters = {
        'expirydate': timestamp,
        'expiryseconds': seconds
    }

    asl_state_machine_definition = {
        "StartAt": first_state_name,
        "States": {
            first_state_name: {
                "Type": "Pass",
                "Next": first_wait_state_name,
                "Parameters": parameters
            },
            first_wait_state_name: {
                "Seconds": seconds,
                "Type": "Wait",
                "Next": second_wait_state_name
            },
            second_wait_state_name: {
                "Timestamp": timestamp,
                "Type": "Wait",
                "Next": third_wait_state_name
            },
            third_wait_state_name: {
                "TimestampPath": timestamp_path,
                "Type": "Wait",
                "Next": fourth_wait_state_name
            },
            fourth_wait_state_name: {
                "SecondsPath": seconds_path,
                "Type": "Wait",
                "Next": final_state_name
            },
            final_state_name: {
                "Type": "Pass",
                "Result": wait_state_result,
                "End": True
            }
        }
    }

    definition = steps.Chain([
        steps.Pass(first_state_name, parameters=parameters),
        steps.Wait(first_wait_state_name, seconds=seconds),
        steps.Wait(second_wait_state_name, timestamp=timestamp),
        steps.Wait(third_wait_state_name, timestamp_path=timestamp_path),
        steps.Wait(fourth_wait_state_name, seconds_path=seconds_path),
        steps.Pass(final_state_name, result=wait_state_result)
    ])

    workflow = Workflow(
        unique_name_from_base('Test_Wait_Workflow'),
        definition=definition,
        role=sfn_role_arn
    )

    workflow_test_suite(sfn_client, workflow, asl_state_machine_definition, wait_state_result)


def test_parallel_state_machine_creation(sfn_client, sfn_role_arn):
    parallel_state_name = "Parallel"
    left_pass_name = "Left Pass"
    right_pass_name = "Right Pass"
    final_state_name = "Final State"
    parallel_state_result = "Parallel Result"

    asl_state_machine_definition = {
        "StartAt": parallel_state_name,
        "States": {
            parallel_state_name: {
                "Type": "Parallel",
                "Next": final_state_name,
                "Branches": [
                    {
                        "StartAt": left_pass_name,
                        "States": {
                            left_pass_name: {
                                "Type": "Pass",
                                "End": True
                            }
                        }
                    },
                    {
                        "StartAt": right_pass_name,
                        "States": {
                            right_pass_name: {
                                "Type": "Pass",
                                "End": True
                            }
                        }
                    }
                ]
            },
            final_state_name: {
                "Type": "Pass",
                "Result": parallel_state_result,
                "End": True
            }
        }
    }
    parallel_waits = steps.Parallel(parallel_state_name)
    parallel_waits.add_branch(steps.Pass(left_pass_name))
    parallel_waits.add_branch(steps.Pass(right_pass_name))

    definition = steps.Chain([
        parallel_waits,
        steps.Pass(final_state_name, result=parallel_state_result)
    ])

    workflow = Workflow(
        unique_name_from_base('Test_Parallel_Workflow'),
        definition=definition,
        role=sfn_role_arn
    )

    workflow_test_suite(sfn_client, workflow, asl_state_machine_definition, parallel_state_result)


def test_map_state_machine_creation(sfn_client, sfn_role_arn):
    map_state_name = "Map State"
    iterated_state_name = "Pass State"
    final_state_name = "Final State"
    items_path = "$.array"
    max_concurrency = 0
    map_state_result = "Map Result"
    state_machine_input = {
        "array": [1, 2, 3]
    }

    asl_state_machine_definition = {
        "StartAt": map_state_name,
        "States": {
            map_state_name: {
                "ItemsPath": items_path,
                "Iterator": {
                    "StartAt": iterated_state_name,
                    "States": {
                        iterated_state_name: {
                            "Type": "Pass",
                            "End": True
                        }
                    }
                },
                "MaxConcurrency": max_concurrency,
                "Type": "Map",
                "Next": final_state_name
            },
            final_state_name: {
                "Type": "Pass",
                "Result": map_state_result,
                "End": True
            }
        }
    }

    map_state = steps.Map(
        map_state_name,
        items_path=items_path,
        iterator=steps.Pass(iterated_state_name),
        max_concurrency=max_concurrency)

    definition = steps.Chain([
        map_state,
        steps.Pass(final_state_name, result=map_state_result)
    ])

    workflow = Workflow(
        unique_name_from_base('Test_Map_Workflow'),
        definition=definition,
        role=sfn_role_arn
    )

    workflow_test_suite(sfn_client, workflow, asl_state_machine_definition, map_state_result, state_machine_input)


def test_choice_state_machine_creation(sfn_client, sfn_role_arn):
    choice_state_name = "ChoiceState"
    first_match_name = "FirstMatchState"
    second_match_name = "SecondMatchState"
    default_state_name = "DefaultState"
    variable = "$.choice"
    first_choice_value = 1
    second_choice_value = 2
    default_error = "DefaultStateError"
    default_cause = "No Matches"
    first_choice_state_result = "First Choice State"
    second_choice_state_result = "Second Choice State"
    state_machine_input = {
        "choice": first_choice_value
    }

    asl_state_machine_definition = {
        "StartAt": choice_state_name,
        "States": {
            choice_state_name: {
                "Type": "Choice",
                "Choices": [
                    {
                        "Variable": variable,
                        "NumericEquals": first_choice_value,
                        "Next": first_match_name
                    },
                    {
                        "Variable": variable,
                        "NumericEquals": second_choice_value,
                        "Next": second_match_name
                    }
                ],
                "Default": default_state_name
            },
            default_state_name: {
                "Error": default_error,
                "Cause": default_cause,
                "Type": "Fail"
            },
            first_match_name: {
                "Type": "Pass",
                "Result": first_choice_state_result,
                "End": True
            },
            second_match_name: {
                "Type": "Pass",
                "Result": second_choice_state_result,
                "End": True
            }
        }
    }

    definition = steps.Choice(choice_state_name)

    definition.default_choice(
        steps.Fail(
            default_state_name,
            error=default_error,
            cause=default_cause
        )
    )
    definition.add_choice(
        steps.ChoiceRule.NumericEquals(
            variable=variable,
            value=first_choice_value
        ),
        steps.Pass(
            first_match_name,
            result=first_choice_state_result
        )
    )
    definition.add_choice(
        steps.ChoiceRule.NumericEquals(
            variable=variable,
            value=second_choice_value
        ),
        steps.Pass(
            second_match_name,
            result=second_choice_state_result
        )
    )

    workflow = Workflow(
        unique_name_from_base('Test_Choice_Workflow'),
        definition=definition,
        role=sfn_role_arn
    )

    workflow_test_suite(sfn_client, workflow, asl_state_machine_definition, first_choice_state_result, state_machine_input)


def test_task_state_machine_creation(sfn_client, sfn_role_arn, training_job_parameters):
    task_state_name = "TaskState"
    final_state_name = "FinalState"
    resource = f"arn:{get_aws_partition()}:states:::sagemaker:createTrainingJob.sync"
    task_state_result = "Task State Result"
    asl_state_machine_definition = {
        "StartAt": task_state_name,
        "States": {
            task_state_name: {
                "Resource": resource,
                "Parameters": training_job_parameters,
                "Type": "Task",
                "Next": final_state_name
            },
            final_state_name: {
                "Type": "Pass",
                "Result" : task_state_result,
                "End": True
            }
        }
    }

    definition = steps.Chain([
        steps.Task(
            task_state_name,
            resource=resource,
            parameters=training_job_parameters
        ),
        steps.Pass(final_state_name, result=task_state_result)
    ])

    workflow = Workflow(
        unique_name_from_base('Test_Task_Workflow'),
        definition=definition,
        role=sfn_role_arn
    )

    workflow_test_suite(sfn_client, workflow, asl_state_machine_definition, task_state_result)


def test_catch_state_machine_creation(sfn_client, sfn_role_arn, training_job_parameters):
    catch_state_name = "TaskWithCatchState"
    task_failed_error = "States.TaskFailed"
    timeout_error = "States.Timeout"
    task_failed_state_name = "Catch Task Failed End"
    timeout_state_name = "Catch Timeout End"
    catch_state_result = "Catch Result"
    task_resource = f"arn:{get_aws_partition()}:states:::sagemaker:createTrainingJob.sync"

    # Provide invalid TrainingImage to cause States.TaskFailed error
    training_job_parameters["AlgorithmSpecification"]["TrainingImage"] = "not_an_image"

    task = steps.Task(
        catch_state_name,
        parameters=training_job_parameters,
        resource=task_resource,
        catch=steps.Catch(
            error_equals=[timeout_error],
            next_step=steps.Pass(timeout_state_name, result=catch_state_result)
        )
    )
    task.add_catch(
        steps.Catch(
            error_equals=[task_failed_error],
            next_step=steps.Pass(task_failed_state_name, result=catch_state_result)
        )
    )

    workflow = Workflow(
        unique_name_from_base('Test_Catch_Workflow'),
        definition=task,
        role=sfn_role_arn
    )

    asl_state_machine_definition = {
        "StartAt": catch_state_name,
        "States": {
            catch_state_name: {
                "Resource": task_resource,
                "Parameters": training_job_parameters,
                "Type": "Task",
                "End": True,
                "Catch": [
                    {
                        "ErrorEquals": [
                            timeout_error
                        ],
                        "Next": timeout_state_name
                    },
                    {
                        "ErrorEquals": [
                            task_failed_error
                        ],
                        "Next": task_failed_state_name
                    }
                ]
            },
            task_failed_state_name: {
                "Type": "Pass",
                "Result": catch_state_result,
                "End": True
            },
            timeout_state_name: {
                "Type": "Pass",
                "Result": catch_state_result,
                "End": True
            },
        }
    }

    workflow_test_suite(sfn_client, workflow, asl_state_machine_definition, catch_state_result)


def test_retry_state_machine_creation(sfn_client, sfn_role_arn, training_job_parameters):
    retry_state_name = "RetryStateName"
    task_failed_error = "States.TaskFailed"
    timeout_error = "States.Timeout"
    interval_seconds = 1
    max_attempts = 2
    backoff_rate = 2
    task_resource = f"arn:{get_aws_partition()}:states:::sagemaker:createTrainingJob.sync"

    # Provide invalid TrainingImage to cause States.TaskFailed error
    training_job_parameters["AlgorithmSpecification"]["TrainingImage"] = "not_an_image"

    task = steps.Task(
        retry_state_name,
        parameters=training_job_parameters,
        resource=task_resource,
        retry=steps.Retry(
            error_equals=[timeout_error],
            interval_seconds=interval_seconds,
            max_attempts=max_attempts,
            backoff_rate=backoff_rate
        )
    )

    task.add_retry(
        steps.Retry(
            error_equals=[task_failed_error],
            interval_seconds=interval_seconds,
            max_attempts=max_attempts,
            backoff_rate=backoff_rate
        )
    )

    workflow = Workflow(
        unique_name_from_base('Test_Retry_Workflow'),
        definition=task,
        role=sfn_role_arn
    )

    asl_state_machine_definition = {
        "StartAt": retry_state_name,
        "States": {
            retry_state_name: {
                "Resource": task_resource,
                "Parameters": training_job_parameters,
                "Type": "Task",
                "End": True,
                "Retry": [
                    {
                        "ErrorEquals": [timeout_error],
                        "IntervalSeconds": interval_seconds,
                        "MaxAttempts": max_attempts,
                        "BackoffRate": backoff_rate
                    },
                    {
                        "ErrorEquals": [task_failed_error],
                        "IntervalSeconds": interval_seconds,
                        "MaxAttempts": max_attempts,
                        "BackoffRate": backoff_rate
                    }
                ]
            }
        }
    }

    workflow_test_suite(sfn_client, workflow, asl_state_machine_definition, None)
