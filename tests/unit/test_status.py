import pytest
from cromshell.status import command as status_command
import os
import json

command_name = "status"


class TestStatus:
    """Test the status command functions"""

    def test_get_all_call_values_doomed(self, mock_data_path):
        global command_name
        function_name = "get_all_call_values"

        workflow_metadata_path = os.path.join(mock_data_path,
                                              "doom_workflow_slim_metadata.json")
        with open(workflow_metadata_path, 'r') as f:
            workflow_metadata = json.load(f)

        workflow_metadata_status_sum_path = os.path.join(mock_data_path,
                                                         command_name,
                                                         function_name,
                                                         "doom_workflow_output.json")
        with open(workflow_metadata_status_sum_path, 'r') as f:
            workflow_metadata_status_sum = json.load(f)

        assert status_command.get_all_call_values(
            workflow_metadata) == workflow_metadata_status_sum, "Output does not match"

    def test_get_all_call_values_running(self, mock_data_path):
        global command_name
        function_name = "get_all_call_values"

        workflow_metadata_path = os.path.join(mock_data_path,
                                              "running_workflow_slim_metadata.json")
        with open(workflow_metadata_path, 'r') as f:
            workflow_metadata = json.load(f)

        workflow_metadata_status_sum_path = os.path.join(mock_data_path,
                                                         command_name,
                                                         function_name,
                                                         "running_workflow_output.json")
        with open(workflow_metadata_status_sum_path, 'r') as f:
            workflow_metadata_status_sum = json.load(f)

        assert status_command.get_all_call_values(
            workflow_metadata) == workflow_metadata_status_sum, "Output does not match"

    def test_get_metadata_status_summary_doom(self, mock_data_path):
        global command_name
        function_name = "get_metadata_status_summary"

        workflow_metadata_path = os.path.join(mock_data_path,
                                              command_name,
                                              function_name,
                                              "doom_workflow_input.json")
        with open(workflow_metadata_path, 'r') as f:
            workflow_metadata = json.load(f)
        workflow_metadata_status_sum_path = os.path.join(mock_data_path,
                                                         command_name,
                                                         function_name,
                                                         "doom_workflow_output.json")
        with open(workflow_metadata_status_sum_path, 'r') as f:
            workflow_metadata_status_sum = json.load(f)

        assert status_command.get_metadata_status_summary(
            workflow_metadata) == workflow_metadata_status_sum, "Output does not match"

    def test_get_metadata_status_summary_running(self, mock_data_path):
        global command_name
        function_name = "get_metadata_status_summary"

        workflow_metadata_path = os.path.join(mock_data_path,
                                              command_name,
                                              function_name,
                                              "running_workflow_input.json")
        with open(workflow_metadata_path, 'r') as f:
            workflow_metadata = json.load(f)
        workflow_metadata_status_sum_path = os.path.join(mock_data_path,
                                                         command_name,
                                                         function_name,
                                                         "running_workflow_output.json")
        with open(workflow_metadata_status_sum_path, 'r') as f:
            workflow_metadata_status_sum = json.load(f)

        assert status_command.get_metadata_status_summary(
            workflow_metadata) == workflow_metadata_status_sum, "Output does not match"

    @pytest.fixture
    def mock_data_path(self):
        return os.path.join(os.path.dirname(__file__), "mock_data/")
