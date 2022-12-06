import json
import os

import pytest
from cromshell.logs import command as logs_command


class TestLogs:
    """Test the Logs command functions"""

    @pytest.mark.parametrize(
        "test_file, status_keys, expect_logs",
        [
            ("success.json", ["Failed"], False),
            ("success.json", ["Done"], True),
            ("will_fail.json", ["Failed"], True),
            ("will_fail.json", ["Failed", "Done"], True),
            ("will_fail.json", ["RetryableFailure"], False),
            ("will_fail.json", ["ALL"], True),
        ],
    )
    def test_workflow_that_is_doomed(
        self, test_file, status_keys, expect_logs, mock_data_path
    ):
        workflow_metadata_path = os.path.join(mock_data_path, test_file)
        with open(workflow_metadata_path, "r") as f:
            workflow_metadata = json.load(f)

        logs_output = logs_command.print_workflow_logs(
            workflow_metadata=workflow_metadata,
            expand_sub_workflows=True,
            indent="",
            status_keys=status_keys,
            cat_logs=False,
        )

        assert logs_output == expect_logs

    @pytest.mark.parametrize(
        "test_file, task, expect_logs",
        [
            (
                "local_helloworld_metadata.json",
                "HelloWorld.HelloWorldTask",
                "Backend Logs Not Available Due to Local Execution",
            ),
            (
                "PAPIV2_helloworld_metadata.json",
                "HelloWorld.HelloWorldTask",
                "gs://broad-dsp-lrma-cromwell-central/HelloWorld/9ee4aa2e-7ac5-4c61-88b2-88a4d10f168b/call-HelloWorldTask/HelloWorldTask.log",
            ),
        ],
    )
    def test_get_backend_logs(self, test_file, task, expect_logs, mock_data_path):
        workflow_metadata_path = os.path.join(mock_data_path, test_file)

        with open(workflow_metadata_path, "r") as f:
            workflow_metadata = json.load(f)

        shard_list = workflow_metadata["calls"][task]

        assert logs_command.get_backend_logs(task_instance=shard_list[0]) == expect_logs

    @pytest.fixture
    def mock_data_path(self):
        return os.path.join(os.path.dirname(__file__), "mock_data/logs/")
