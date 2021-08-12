# Contributing Guidelines

Thank you for your interest in contributing to our project. Whether it's a bug report, new feature, correction, or additional
documentation, we greatly value feedback and contributions from our community.

Please read through this document before submitting any issues or pull requests to ensure we have all the necessary
information to effectively respond to your bug report or contribution.


## Table of Contents

* [Table of Contents](#table-of-contents)
* [Reporting Bugs/Feature Requests](#reporting-bugsfeature-requests)
* [Contributing via Pull Requests (PRs)](#contributing-via-pull-requests-prs)
  * [Pulling Down the Code](#pulling-down-the-code)
  * [Running the Unit Tests](#running-the-unit-tests)
    * [Running Unit Tests and Debugging in PyCharm](#running-unit-tests-and-debugging-in-pycharm)
  * [Running the Integration Tests](#running-the-integration-tests)
  * [Making and Testing Your Change](#making-and-testing-your-change)
  * [Committing Your Change](#committing-your-change)
  * [Sending a Pull Request](#sending-a-pull-request)
* [Finding Contributions to Work On](#finding-contributions-to-work-on)
* [Setting Up Your Development Environment](#setting-up-your-development-environment)
  * [Setting Up Your Environment for Debugging](#setting-up-your-environment-for-debugging)
    * [PyCharm](#pycharm)
* [Code of Conduct](#code-of-conduct)
* [Security Issue Notifications](#security-issue-notifications)
* [Licensing](#licensing)

## Reporting Bugs/Feature Requests

We welcome you to use the GitHub issue tracker to report bugs or suggest features.

When filing an issue, please check [existing open](https://github.com/aws/aws-step-functions-data-science-sdk-python/issues) and [recently closed](https://github.com/aws/aws-step-functions-data-science-sdk-python/issues?utf8=%E2%9C%93&q=is%3Aissue%20is%3Aclosed%20) issues to make sure somebody else hasn't already
reported the issue. Please try to include as much information as you can. Details like these are incredibly useful:

* A reproducible test case or series of steps.
* The version of our code being used.
* Any modifications you've made relevant to the bug.
* A description of your environment or deployment.


## Contributing via Pull Requests (PRs)

Contributions via pull requests are much appreciated.

Before sending us a pull request, please ensure that:

* You are working against the latest source on the *main* branch.
* You check the existing open and recently merged pull requests to make sure someone else hasn't already addressed the problem.
* You open an issue to discuss any significant work - we would hate for your time to be wasted.

### Pulling Down the Code

1. If you do not already have one, create a GitHub account by following the prompts at [Join Github](https://github.com/join).
1. Create a fork of this repository on GitHub. You should end up with a fork at `https://github.com/<username>/aws-step-functions-data-science-sdk-python`.
   1. Follow the instructions at [Fork a Repo](https://help.github.com/en/articles/fork-a-repo) to fork a GitHub repository.
1. Clone your fork of the repository: `git clone https://github.com/<username>/aws-step-functions-data-science-sdk-python` where `<username>` is your github username.


### Running the Unit Tests

1. Install tox using `pip install tox`
1. cd into the aws-step-functions-data-science-sdk-python folder: `cd aws-step-functions-data-science-sdk-python` or `cd /environment/aws-step-functions-data-science-sdk-python`
1. Install test dependencies, including coverage, using `pip install ".[test]"`
1. Run the following tox command and verify that all code checks and unit tests pass: `tox tests/unit`

You can also run a single test with the following command: `tox -e py36 -- -s -vv <path_to_file><file_name>::<test_function_name>`
  * Note that the coverage test will fail if you only run a single test, so make sure to surround the command with `export IGNORE_COVERAGE=-` and `unset IGNORE_COVERAGE`
  * Example: `export IGNORE_COVERAGE=- ; tox -e py36 -- -s -vv tests/unit/test_sagemaker_steps.py::test_training_step_creation_with_model ; unset IGNORE_COVERAGE`

#### Running Unit Tests and Debugging in PyCharm
You can also run the unit tests with the following options:
* Right click on a test file in the Project tree and select `Run/Debug 'pytest' for ...`
* Right click on the test definition and select `Run/Debug 'pytest' for ...`
* Click on the green arrow next to test definition

### Running the Integration Tests

Our CI system runs integration tests (the ones in the `tests/integ` directory), in parallel, for every Pull Request.
You should only worry about manually running any new integration tests that you write, or integration tests that test an area of code that you've modified.
#### Setup

If you haven't done so already, install tox and test dependencies:
1. `pip install tox`
1. `pip install .[test]`

#### AWS Credentials
Follow the instructions at [Set Up the AWS Command Line Interface (AWS CLI)](https://docs.aws.amazon.com/polly/latest/dg/setup-aws-cli.html).
#### Create IAM Roles

The tests use two IAM roles to give Step Functions and SageMaker permissions to access AWS resources in your account. Use the following commands in the root directory of this repository:

```bash
aws iam create-role \
   --role-name StepFunctionsMLWorkflowExecutionFullAccess \
   --assume-role-policy-document file://tests/integ/resources/StepFunctionsMLWorkflowExecutionFullAccess-TrustPolicy.json
```

```bash
aws iam put-role-policy \
   --role-name StepFunctionsMLWorkflowExecutionFullAccess \
   --policy-name StepFunctionsMLWorkflowExecutionFullAccess \
   --policy-document file://tests/integ/resources/StepFunctionsMLWorkflowExecutionFullAccess-Policy.json
```

```bash
aws iam create-role \
   --role-name SageMakerRole \
   --assume-role-policy-document file://tests/integ/resources/SageMaker-TrustPolicy.json
```

```bash
aws iam attach-role-policy \
   --role-name SageMakerRole \
   --policy-arn arn:aws:iam::aws:policy/AmazonSageMakerFullAccess
```
#### Execute the tests
1. To run a test, specify the test file and method you want to run per the following command: `tox -e py36 -- -s -vv <path_to_file><file_name>::<test_function_name>`
   * Note that the coverage test will fail if you only run a single test, so make sure to surround the command with `export IGNORE_COVERAGE=-` and `unset IGNORE_COVERAGE`
   * Example: `export IGNORE_COVERAGE=- ; tox -e py36 -- -s -vv tests/integ/test_state_machine_definition.py::test_wait_state_machine_creation ; unset IGNORE_COVERAGE`
1. To run all integration tests, run the following command: `tox tests/integ`

### Making and Testing Your Change

1. Create a new git branch:
     ```shell
     git checkout -b my-fix-branch
     ```
1. Make your changes, **including unit tests** and, if appropriate, integration tests.
   1. Include unit tests when you contribute new features or make bug fixes, as they help to:
      1. Prove that your code works correctly.
      1. Guard against future breaking changes to lower the maintenance cost.
   1. Please focus on the specific change you are contributing. If you also reformat all the code, it will be hard for us to focus on your change.
1. Run all the unit tests as per [Running the Unit Tests](#running-the-unit-tests), and verify that all checks and tests pass.
   1. Note that this also runs tools that may be necessary for the automated build to pass (ex: code reformatting by 'black').


### Committing Your Change

We use commit messages to update the project version number and generate changelog entries, so it's important for them to follow the right format. Valid commit messages include a prefix, separated from the rest of the message by a colon and a space. Here are a few examples:

```
feature: support VPC config for hyperparameter tuning
fix: fix flake8 errors
documentation: add MXNet documentation
```

Valid prefixes are listed in the table below.

| Prefix          | Use for...                                                                                     |
|----------------:|:-----------------------------------------------------------------------------------------------|
| `breaking`      | Incompatible API changes.                                                                      |
| `deprecation`   | Deprecating an existing API or feature, or removing something that was previously deprecated.  |
| `feature`       | Adding a new feature.                                                                          |
| `fix`           | Bug fixes.                                                                                     |
| `change`        | Any other code change.                                                                         |
| `documentation` | Documentation changes.                                                                         |

Some of the prefixes allow abbreviation ; `break`, `feat`, `depr`, and `doc` are all valid. If you omit a prefix, the commit will be treated as a `change`.

For the rest of the message, use imperative style and keep things concise but informative. See [How to Write a Git Commit Message](https://chris.beams.io/posts/git-commit/) for guidance.


### Sending a Pull Request

GitHub provides additional document on [Creating a Pull Request](https://help.github.com/articles/creating-a-pull-request/).

Please remember to:
* Use commit messages (and PR titles) that follow the guidelines under [Committing Your Change](#committing-your-change).
* Send us a pull request, answering any default questions in the pull request interface.
* Pay attention to any automated CI failures reported in the pull request, and stay involved in the conversation.


## Finding Contributions to Work On

Looking at the existing issues is a great way to find something to contribute on. As our projects, by default, use the default GitHub issue labels ((enhancement/bug/duplicate/help wanted/invalid/question/wontfix), looking at any ['help wanted'](https://github.com/aws/aws-step-functions-data-science-sdk-python/labels/help%20wanted) issues is a great place to start.


## Setting Up Your Development Environment

### Setting Up Your Environment for Debugging

Setting up your IDE for debugging tests locally will save you a lot of time.
You might be able to `Run` and `Debug` the tests directly in your IDE with your default settings, but if it's not the case,
follow the steps described in this section.

#### PyCharm
1. Set your Default test runner to `pytest` in _Preferences → Tools → Python Integrated Tools_
1. If you are using `PyCharm Professional Edition`, go to _Preferences → Build, Execution, Deployment → Python Debugger_ and set the options with following values:
   
   | Option                                                      | Value                 |
   |:------------------------------------------------------------ |:----------------------|
   | Attach subprocess automatically while debugging             | `Enabled`             |
   | Collect run-time types information for code insight         | `Enabled`             |
   | Gevent compatible                                           | `Disabled`            |
   | Drop into debugger on failed tests                          | `Enabled`             |
   | PyQt compatible                                             | `Auto`                |
   | For Attach to Process show processes with names containing  | `python`              |
   
    This will allow you to break into all subprocesses of the process being debugged and preserve functions types while debugging.
1. Debug tests in PyCharm as per [Running Unit Tests and Debugging in PyCharm](#running-unit-tests-and-debugging-in-pycharm)

_Note: This setup was tested and confirmed to work with
`PyCharm 2020.3.5 (Professional Edition)` and `PyCharm 2021.1.1 (Professional Edition)`_

## Code of Conduct

This project has adopted the [Amazon Open Source Code of Conduct](https://aws.github.io/code-of-conduct).
For more information see the [Code of Conduct FAQ](https://aws.github.io/code-of-conduct-faq) or contact
opensource-codeofconduct@amazon.com with any additional questions or comments.


## Security Issue Notifications

If you discover a potential security issue in this project we ask that you notify AWS/Amazon Security via our [vulnerability reporting page](http://aws.amazon.com/security/vulnerability-reporting/). Please do **not** create a public github issue.


## Licensing

See the [LICENSE](https://github.com/aws/aws-step-functions-data-science-sdk-python/blob/main/LICENSE) file for our project's licensing. We will ask you to confirm the licensing of your contribution.

We may ask you to sign a [Contributor License Agreement (CLA)](http://en.wikipedia.org/wiki/Contributor_License_Agreement) for larger changes.
