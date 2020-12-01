from cromshell.utilities import cromshellconfig
from importlib import reload
from pathlib import Path
import pytest
import os


class TestCromshellConfig:
    """Test the cromshell config functions and variables"""

    def test_override_slim_metadata_parameters(self):
        reload(cromshellconfig)
        default_slim_parameters = (
            "=includeKey=id&includeKey=executionStatus&includeKey=backendStatus"
            "&includeKey=status&includeKey=callRoot&expandSubWorkflows=true&includeKey"
            "=subWorkflowMetadata&includeKey=subWorkflowId"
        )
        assert cromshellconfig.slim_metadata_parameters == default_slim_parameters, \
            "By default slim_metadata_parameters should equal \n" \
            "{slim_metadata_parameters}"

        test_slim_parameters = (
                "expandSubWorkflows=true"
                + "&includeKey=subWorkflowMetadata&includeKey=subWorkflowId"
        )
        cromshellconfig.override_slim_metadata_parameters("expandSubWorkflows=true")
        assert cromshellconfig.slim_metadata_parameters == test_slim_parameters, \
            "Slim metadata parameters should be set to the" \
            "following after being specified \n" \
            f"{test_slim_parameters}"

    def test_resolve_cromwell_config_server_address(self):
        reload(cromshellconfig)
        test_cromwell_url = "https://cromwell-v1.dsde-methods.broadinstitute.org"

        assert cromshellconfig.cromwell_server is not None, \
            "Cromwell server variable should not be empty"

        cromshellconfig.resolve_cromwell_config_server_address(
            server_user=test_cromwell_url)
        assert cromshellconfig.cromwell_server == test_cromwell_url, \
            f"Cromwell server variable should be set to the specified server url : {test_cromwell_url}"

    def test_resolve_cromwell_config_server_address_with_mock_data(self, mock_data_path):
        reload(cromshellconfig)
        test_cromwell_url = "https://cromwell-v1.dsde-methods.broadinstitute.org"
        mock_workflow_id = "d689adec-c600-4e4b-be37-4e30e65848c7"
        mock_cromwell_url = "https://cromwell-v45.dsde-methods.broadinstitute.org"

        # Set the submission file path to mock data
        cromshellconfig.submission_file = os.path.join(mock_data_path,
                                                       "all.workflow.database.tsv")
        # Execute function that changes cromwell server based off the
        # workflow id and submission file
        cromshellconfig.resolve_cromwell_config_server_address(
            workflow_id=mock_workflow_id)
        assert cromshellconfig.cromwell_server == mock_cromwell_url, \
            f"Cromwell server variable should be set to {mock_cromwell_url}"

        # Cromwell url parameter should supersede workflow id look up
        cromshellconfig.resolve_cromwell_config_server_address(
            server_user=test_cromwell_url,
            workflow_id=mock_workflow_id)
        assert cromshellconfig.cromwell_server == test_cromwell_url, \
            f"Cromwell server variable should be set to {test_cromwell_url}"

    def test_config_dir(self):
        reload(cromshellconfig)
        assert cromshellconfig.config_dir is not None, "Config variable should be set"

        assert cromshellconfig.config_dir == os.path.join(Path.home(), ".cromshell"), \
            "Config file variable path should be in .cromshell"

        assert Path(cromshellconfig.config_dir).exists(), \
            "Config directory should exist "

    def test_submission_file(self):
        reload(cromshellconfig)
        assert cromshellconfig.submission_file is not None, \
            "Submission file variable should be set "

        path_to_submission = os.path.join(Path.home(), ".cromshell",
                                          "all.workflow.database.tsv")
        assert cromshellconfig.submission_file == path_to_submission, \
            f"Submission file path should be {path_to_submission} "

        assert Path(cromshellconfig.submission_file).exists(), \
            "Submission file should exist"

    def test_cromwell_server(self):
        reload(cromshellconfig)
        assert cromshellconfig.cromwell_server is not None, \
            "Cromwell server should be set"

    @pytest.fixture
    def mock_data_path(self):
        return os.path.join(os.path.dirname(__file__), "mock_data/")
