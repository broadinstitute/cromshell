import json
import os

import pytest

from cromshell.status import command as status_command


class TestStatus:
    """Test the status command functions"""

    def test_workflow_failed_for_metadata_that_is_doomed(self, mock_data_path):
        workflow_metadata_path = os.path.join(
            mock_data_path, "doom_workflow_slim_metadata.json"
        )
        with open(workflow_metadata_path, "r") as f:
            workflow_metadata = json.load(f)

        assert status_command.workflow_failed(workflow_metadata) is True, (
            "A running doomed workflow metadata should have "
            "output 'True' to indicate workflow "
            "has failed."
        )

    def test_workflow_failed_for_metadata_that_is_running(self, mock_data_path):
        workflow_metadata_path = os.path.join(
            mock_data_path, "running_workflow_slim_metadata.json"
        )
        with open(workflow_metadata_path, "r") as f:
            workflow_metadata = json.load(f)

        assert status_command.workflow_failed(workflow_metadata) is False, (
            "A running workflow metadata should have "
            "output 'False' to indicate workflow is "
            "still running."
        )

    @pytest.fixture
    def mock_data_path(self):
        return os.path.join(os.path.dirname(__file__), "mock_data/")
