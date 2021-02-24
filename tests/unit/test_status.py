import pytest
from cromshell.status import command as status_command
import os
import json


class TestStatus:
    """Test the status command functions"""

    def test_check_for_failure_doom(self, mock_data_path):
        workflow_metadata_path = os.path.join(
            mock_data_path, "doom_workflow_slim_metadata.json"
        )
        with open(workflow_metadata_path, "r") as f:
            workflow_metadata = json.load(f)

        assert status_command.check_for_failure(workflow_metadata) == "True", (
            "A running workflow metadata should have "
            "output 'True' to indicate workflow "
            "has failed."
        )

    def test_check_for_failure_running(self, mock_data_path):
        workflow_metadata_path = os.path.join(
            mock_data_path, "running_workflow_slim_metadata.json"
        )
        with open(workflow_metadata_path, "r") as f:
            workflow_metadata = json.load(f)

        assert status_command.check_for_failure(workflow_metadata) == "False", (
            "A running workflow metadata should have "
            "output 'False' to indicate workflow is "
            "still running."
        )

    @pytest.fixture
    def mock_data_path(self):
        return os.path.join(os.path.dirname(__file__), "mock_data/")
