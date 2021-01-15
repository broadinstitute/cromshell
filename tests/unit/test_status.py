import pytest
from cromshell.status import command as status_command
import os
import json


class TestStatus:
    """Test the status command functions"""

    def test_get_all_call_values_doomed(self, mock_data_path):
        workflow_metadata_path = os.path.join(mock_data_path,
                                              "doom_workflow_slim_metadata.json")
        with open(workflow_metadata_path, 'r') as f:
            workflow_metadata = json.load(f)
        workflow_metadata_status_sum_path = os.path.join(mock_data_path,
                                                         "status/get_all_call_values/doom_workflow_output.json")
        with open(workflow_metadata_status_sum_path, 'r') as f:
            workflow_metadata_status_sum = json.load(f)

        assert status_command.get_metadata_status_summary(
            workflow_metadata) == workflow_metadata_status_sum, "Output does not match"

    def test_get_metadata_status_summary_failed(self, mock_data_path):
        workflow_metadata_path = os.path.join(mock_data_path,
                                              "fail_workflow_slim_metadata.json")
        with open(workflow_metadata_path, 'r') as f:
            workflow_metadata = json.load(f)
        workflow_metadata_status_sum_path = os.path.join(mock_data_path,
                                                         "failed_workflow_status_summary.json")
        with open(workflow_metadata_status_sum_path, 'r') as f:
            workflow_metadata_status_sum = json.load(f)

        assert status_command.get_metadata_status_summary(
            workflow_metadata) == workflow_metadata_status_sum, "Output does not match"

    def test_get_metadata_status_summary_running(self, mock_data_path):
        workflow_metadata_path = os.path.join(mock_data_path,
                                              "running_workflow_slim_metadata.json")
        with open(workflow_metadata_path, 'r') as f:
            workflow_metadata = json.load(f)
        workflow_metadata_status_sum_path = os.path.join(mock_data_path,
                                                         "running_workflow_status_summary.json")
        with open(workflow_metadata_status_sum_path, 'r') as f:
            workflow_metadata_status_sum = json.load(f)

        assert status_command.get_metadata_status_summary(
            workflow_metadata) == workflow_metadata_status_sum, "Output does not match"

    @pytest.fixture
    def mock_data_path(self):
        return os.path.join(os.path.dirname(__file__), "mock_data/")
