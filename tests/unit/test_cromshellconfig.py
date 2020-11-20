from pathlib import Path
from cromshell.utilities import cromshellconfig
import pytest
import os


class TestCromshellConfig:
    """Test the cromshell config values"""

    def test_override_slim_metadata_parameters(self):
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

    def test_resolve_cromwell_config_server_address(self, mock_data):

        assert cromshellconfig.cromwell_server is not None, \
            "Cromwell server variable should be set"

        cromshellconfig.resolve_cromwell_config_server_address(server_user="https://cromwell-v1.dsde-methods.broadinstitute.org")
        assert cromshellconfig.cromwell_server == "https://cromwell-v1.dsde-methods.broadinstitute.org", \
            "Cromwell server variable should be set to the specified server url "

        # Save the default submission file path in temp variable
        temp_submission_file = cromshellconfig.submission_file
        # Set the submission file path to mock data
        cromshellconfig.submission_file = mock_data
        # Execute function that changes cromwell server based off the
        # workflow id and submission file
        cromshellconfig.resolve_cromwell_config_server_address(workflow_id="d689adec-c600-4e4b-be37-4e30e65848c7")
        assert cromshellconfig.cromwell_server == "https://cromwell-v45.dsde-methods.broadinstitute.org", \
             "Cromwell server variable should be set to https://cromwell-v45.dsde-methods.broadinstitute.org"
        cromshellconfig.submission_file = temp_submission_file

    def test_config_dir(self):
        assert cromshellconfig.config_dir is not None, "Config variable should be set"

        assert cromshellconfig.config_dir == os.path.join(Path.home(), ".cromshell"), \
            "Config file variable path should be in .cromshell"

        assert Path(cromshellconfig.config_dir).exists(), \
            "Config directory should exist "

    def test_submission_file(self):
        assert cromshellconfig.submission_file is not None, \
            "Submission file variable should be set "

        path_to_submission = os.path.join(Path.home(), ".cromshell",
                                          "all.workflow.database.tsv")
        assert cromshellconfig.submission_file == path_to_submission, \
            f"Submission file path should be {path_to_submission} "

        assert Path(cromshellconfig.submission_file).exists(), \
            "Submission file should exist"

    def test_cromwell_server(self):
        cromshell_config = cromshellconfig
        ret_val = 0
        if cromshell_config.cromwell_server is None:
            ret_val = 1

        assert ret_val == 0, "Return value should be 0"

    @pytest.fixture
    def mock_data(self):
        return "tests/unit/mock_data/all.workflow.database.tsv"
