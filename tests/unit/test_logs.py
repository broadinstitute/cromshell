import json
import os

import pytest

from cromshell.logs import command as logs_command


class TestLogs:
    """Test the Logs command functions"""

    @pytest.mark.parametrize(
        "test_file, status_keys, expect_logs",
        [
            ("success.json", ["Failure"], False),
            ("success.json", ["Done"], True),
            ("will_fail.json", ["Failure"], True),
            ("will_fail.json", ["Failure", "Done"], True),
            ("will_fail.json", ["RetryableFailure"], False),
            ("will_fail.json", ["ALL"], False),
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

        # We should have found a failing output to print
        assert logs_output == expect_logs

    @pytest.fixture
    def mock_data_path(self):
        return os.path.join(os.path.dirname(__file__), "mock_data/logs/")
