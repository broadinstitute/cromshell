import json
import os

import pytest

from cromshell.logs import command as logs_command


class TestLogs:
    """Test the Logs command functions"""

    @pytest.mark.parametrize(
        "test_file, status_keys, expect_logs",
        [
            ("success.json", ["Done"], {'HelloWorld.HelloWorldTask': [
                {'attempt': 1, 'backend': None,
                 'backendLogs': 'gs://broad-methods-cromwell-exec-bucket-instance-8/HelloWorld/261ee81a-b6c4-4547-8373-4c879eb24858/call-HelloWorldTask/HelloWorldTask.log',
                 'executionStatus': 'Done', 'shardIndex': -1, 'stderr': None,
                 'stdout': None}], }),
            ("will_fail.json", ["Failed"], {'WillFailTester.FailFastTask': [
                {'attempt': 1, 'backend': None,
                 'backendLogs': 'gs://broad-methods-cromwell-exec-bucket-instance-8/WillFailTester/019d7962-4c0c-4651-87ac-b90efff26ff6/call-FailFastTask/FailFastTask.log',
                 'executionStatus': 'Failed', 'shardIndex': -1, 'stderr': None,
                 'stdout': None}], 'WillFailTester.PassRunsLong': [], }),
            ("will_fail.json", ["Failed", "Done"], {'WillFailTester.FailFastTask': [
                {'attempt': 1, 'backend': None,
                 'backendLogs': 'gs://broad-methods-cromwell-exec-bucket-instance-8/WillFailTester/019d7962-4c0c-4651-87ac-b90efff26ff6/call-FailFastTask/FailFastTask.log',
                 'executionStatus': 'Failed', 'shardIndex': -1, 'stderr': None,
                 'stdout': None}], 'WillFailTester.PassRunsLong': [
                {'attempt': 1, 'backend': None,
                 'backendLogs': 'gs://broad-methods-cromwell-exec-bucket-instance-8/WillFailTester/019d7962-4c0c-4651-87ac-b90efff26ff6/call-PassRunsLong/PassRunsLong.log',
                 'executionStatus': 'Done', 'shardIndex': -1, 'stderr': None,
                 'stdout': None}], }),
            # ("will_fail.json", ["RetryableFailure"], "Exception: No logs found for workflow: 019d7962-4c0c-4651-87ac-b90efff26ff6 with status: ['RetryableFailure']"),
            ("will_fail.json", ["ALL"], {'WillFailTester.FailFastTask': [
                {'attempt': 1, 'backend': None,
                 'backendLogs': 'gs://broad-methods-cromwell-exec-bucket-instance-8/WillFailTester/019d7962-4c0c-4651-87ac-b90efff26ff6/call-FailFastTask/FailFastTask.log',
                 'executionStatus': 'Failed', 'shardIndex': -1, 'stderr': None,
                 'stdout': None}], 'WillFailTester.PassRunsLong': [
                {'attempt': 1, 'backend': None,
                 'backendLogs': 'gs://broad-methods-cromwell-exec-bucket-instance-8/WillFailTester/019d7962-4c0c-4651-87ac-b90efff26ff6/call-PassRunsLong/PassRunsLong.log',
                 'executionStatus': 'Done', 'shardIndex': -1, 'stderr': None,
                 'stdout': None}], }),
        ],
    )
    def test_filter_task_logs_from_workflow_metadata(
            self, test_file, status_keys, expect_logs, mock_data_path
    ):
        workflow_metadata_path = os.path.join(mock_data_path, test_file)
        with open(workflow_metadata_path, "r") as f:
            workflow_metadata = json.load(f)

        logs_output = logs_command.filter_task_logs_from_workflow_metadata(
            workflow_metadata=workflow_metadata,
            requested_status=status_keys,
        )

        assert logs_output == expect_logs

    @pytest.mark.parametrize(
        "test_file, status_keys, expect_logs",
        [

            ("success.json", ["Failed"],
             "No logs found for workflow: 261ee81a-b6c4-4547-8373-4c879eb24858 with status: ['Failed']"),
            ("will_fail.json", ["RetryableFailure"],
             "No logs found for workflow: 019d7962-4c0c-4651-87ac-b90efff26ff6 with status: ['RetryableFailure']"),
        ],
    )
    def test_filter_task_logs_from_workflow_metadata_failure(
            self, test_file, status_keys, expect_logs, mock_data_path
    ):
        workflow_metadata_path = os.path.join(mock_data_path, test_file)
        with open(workflow_metadata_path, "r") as f:
            workflow_metadata = json.load(f)

        with pytest.raises(Exception) as e:
            logs_command.filter_task_logs_from_workflow_metadata(
                workflow_metadata=workflow_metadata,
                requested_status=status_keys,
            )

        assert str(e.value) == expect_logs

    @pytest.mark.parametrize(
        "all_task_log_metadata,  expect_logs",
        [
            (
                    {'HelloWorld.HelloWorldTask': [
                        {'attempt': 1, 'backend': None,
                         'backendLogs': 'gs://broad-methods-cromwell-exec-bucket-instance-8/HelloWorld/261ee81a-b6c4-4547-8373-4c879eb24858/call-HelloWorldTask/HelloWorldTask.log',
                         'executionStatus': 'Done', 'shardIndex': -1, 'stderr': None,
                         'stdout': None}],
                    },
                    "HelloWorld.HelloWorldTask:\n\tstatus: Done\x1b[0m\n\tbackendLogs: gs://broad-methods-cromwell-exec-bucket-instance-8/HelloWorld/261ee81a-b6c4-4547-8373-4c879eb24858/call-HelloWorldTask/HelloWorldTask.log\x1b[0m\n",
            )
        ]
    )
    def test_print_task_level_logs(self, all_task_log_metadata, expect_logs, capsys):
        logs_command.print_task_level_logs(
            all_task_log_metadata=all_task_log_metadata,
            cat_logs=False,
        )
        captured = capsys.readouterr()
        assert captured.out == expect_logs

    @pytest.mark.parametrize(
        "task_log_metadata, expect_logs",
        [
            (
                    {
                        'attempt': 1, 'backend': None,
                        'backendLogs': 'gs://broad-methods-cromwell-exec-bucket-instance-8/HelloWorld/261ee81a-b6c4-4547-8373-4c879eb24858/call-HelloWorldTask/HelloWorldTask.log',
                        'executionStatus': 'Done', 'shardIndex': -1, 'stderr': None,
                        'stdout': None,
                    },
                    "\tstatus: Done\x1b[0m\n\tbackendLogs: gs://broad-methods-cromwell-exec-bucket-instance-8/HelloWorld/261ee81a-b6c4-4547-8373-4c879eb24858/call-HelloWorldTask/HelloWorldTask.log\x1b[0m\n",
            )
        ]
    )
    def test_print_file_like_value_in_dict(self, task_log_metadata, expect_logs,
                                           capsys):
        logs_command.print_file_like_value_in_dict(
            task_log_metadata=task_log_metadata,
            indent=1,
            cat_logs=False,
        )
        captured = capsys.readouterr()
        assert captured.out == expect_logs

    @pytest.mark.parametrize(
        "output_name, output_value, indent, expect_logs",
        [
            (
                    "bla",
                    "/bla/bla.txt",
                    0,
                    "bla: /bla/bla.txt\x1b[0m\n",
            ),
            (  # Test when output is string but not file like
                    "bla",
                    "not a file",
                    0,
                    "",
            ),
            (  # Test when output is a float
                    "bla",
                    0.0,
                    0,
                    "",
            ),
        ],
    )
    def test_print_output_name_and_file(
            self,
            output_name,
            output_value,
            indent,
            expect_logs,
            capsys,
    ):
        logs_command.print_output_name_and_file(
            output_name=output_name,
            output_value=output_value,
            indent=indent,
            txt_color=None,
        )
        captured = capsys.readouterr()
        assert captured.out == expect_logs

    @pytest.mark.parametrize(
        "output_name, output_value",
        [
            (
                    "fileName",
                    "./mock_data/logs/success.json",
            ),
        ]
    )
    def test_print_log_file_content(
            self, output_name, output_value, capsys
    ):
        with open(output_value, "r") as f:
            file_content = f.read()
        logs_command.print_log_file_content(
            output_name=output_name,
            output_value=output_value,
            txt_color=None,
            backend="Local",
        )
        captured = capsys.readouterr()
        assert file_content in captured.out

    @pytest.mark.parametrize(
        "workflow_logs, workflow_id, requested_status",
        [
            (
                {'HelloWorld.HelloWorldTask': [
                        {'attempt': 1, 'backend': None,
                         'backendLogs': 'gs://broad-methods-cromwell-exec-bucket-instance-8/HelloWorld/261ee81a-b6c4-4547-8373-4c879eb24858/call-HelloWorldTask/HelloWorldTask.log',
                         'executionStatus': 'Done', 'shardIndex': -1, 'stderr': None,
                         'stdout': None}
                    ],
                }
                , "261ee81a-b6c4-4547-8373-4c879eb24858", "Done"
            ),
            (
                    {'HelloWorld.HelloWorldTask': [
                        {'attempt': 1, 'backend': 'TES',
                         'executionStatus': 'Done', 'shardIndex': -1, 'stderr': None,
                         'stdout': None}
                    ],
                    }
                    , "261ee81a-b6c4-4547-8373-4c879eb24858", "Done"
            ),

        ]
    )
    def test_check_for_empty_logs(
        self, workflow_logs: dict, workflow_id: str, requested_status
    ):
        logs_command.check_for_empty_logs(
            workflow_logs=workflow_logs,
            workflow_id=workflow_id,
            requested_status=requested_status,
        )

    @pytest.mark.parametrize(
        "workflow_logs, workflow_id, requested_status",
        [
            (
                    {'HelloWorld.HelloWorldTask': [
                        {'attempt': 1, 'backend': None,
                         'executionStatus': 'Done', 'shardIndex': -1, 'stderr': None,
                         'stdout': None}
                    ],
                    }
                    , "261ee81a-b6c4-4547-8373-4c879eb24858", "Done"
            ),
            (
                    {}
                    , "261ee81a-b6c4-4547-8373-4c879eb24858", "Done"
            ),

        ]
    )
    def test_check_for_empty_logs_failure(
            self, workflow_logs: dict, workflow_id: str, requested_status
    ):
        if workflow_logs:
            expected_error = f"No logs found for workflow: {workflow_id} with status: " \
                             f"{requested_status}"
        else:
            expected_error = f"No calls found for workflow: {workflow_id}"

        with pytest.raises(Exception) as e:
            logs_command.check_for_empty_logs(
                workflow_logs=workflow_logs,
                workflow_id=workflow_id,
                requested_status=requested_status,
            )

        assert str(e.value) == expected_error

    @pytest.mark.parametrize(
        "task_instance ",
        [
            (
                {'attempt': 1, 'backend': 'PAPI_V2',
                'backendLogs': {'log': 'gs://broad-methods-cromwell-exec-bucket-instance-8/HelloWorld/261ee81a-b6c4-4547-8373-4c879eb24858/call-HelloWorldTask/HelloWorldTask.log'},
                'executionStatus': 'Done', 'shardIndex': -1, 'stderr': None,
                'stdout': None}
            ),
            (
                {'attempt': 1, 'backend': 'PAPI_V2',
                 'executionStatus': 'Done', 'shardIndex': -1, 'stderr': None,
                 'stdout': None}
            ),
            (
                {'attempt': 1, 'backend': 'Local',
                 'backendLogs': {
                     'log': 'gs://broad-methods-cromwell-exec-bucket-instance-8/HelloWorld/261ee81a-b6c4-4547-8373-4c879eb24858/call-HelloWorldTask/HelloWorldTask.log'},
                 'executionStatus': 'Done', 'shardIndex': -1, 'stderr': None,
                 'stdout': None}
            ),
        ]

    )
    def test_get_backend_logs(self, task_instance: dict):

        backend_log = logs_command.get_backend_logs(task_instance=task_instance)
        if task_instance["backend"] == "Local":
            assert backend_log == "Backend Logs Not Available Due to Local Execution"
        elif task_instance["backend"] != "Local" and "backendLogs" not in task_instance:
            assert backend_log == "Backend Logs Not Found"
        else:
            assert backend_log == task_instance["backendLogs"]["log"]


    @pytest.fixture
    def mock_data_path(self):
        return os.path.join(os.path.dirname(__file__), "mock_data/logs/")
