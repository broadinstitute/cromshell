from cromshell.utilities import cromshellconfig
from importlib import reload
from pathlib import Path
import pytest
import os


def reset_cromshellconfig(mock_data_path):
    reload(cromshellconfig)

    # Set the submission file path to mock data
    cromshellconfig.submission_file_path = os.path.join(
        mock_data_path, cromshellconfig.submission_file_name
    )


class TestCromshellConfig:
    """Test the cromshell config functions and variables"""

    def test_override_slim_metadata_parameters(self):
        reload(cromshellconfig)
        default_slim_parameters = (
            "=includeKey=id&includeKey=executionStatus&includeKey=backendStatus"
            "&includeKey=status&includeKey=callRoot&expandSubWorkflows=true&includeKey"
            "=subWorkflowMetadata&includeKey=subWorkflowId"
        )
        assert cromshellconfig.slim_metadata_parameters == default_slim_parameters, (
            "By default slim_metadata_parameters should equal \n"
            "{slim_metadata_parameters}"
        )

        test_slim_parameters = (
                "expandSubWorkflows=true"
                + "&includeKey=subWorkflowMetadata&includeKey=subWorkflowId"
        )
        cromshellconfig.override_slim_metadata_parameters("expandSubWorkflows=true")
        assert cromshellconfig.slim_metadata_parameters == test_slim_parameters, (
            "Slim metadata parameters should be set to the"
            "following after being specified \n"
            f"{test_slim_parameters}"
        )

    def test_resolve_cromwell_config_server_address_not_empty(self):
        reload(cromshellconfig)

        assert (
                cromshellconfig.cromwell_server is not None
        ), "Cromwell server variable should not be empty"

    def test_resolve_cromwell_config_server_address_provided_server_url(
            self, mock_data_path
    ):
        reset_cromshellconfig(mock_data_path)

        test_cromwell_url = "https://cromwell-v1.dsde-methods.broadinstitute.org"

        # Test when server only is given to function
        cromshellconfig.resolve_cromwell_config_server_address(
            server_user=test_cromwell_url
        )
        assert (
                cromshellconfig.cromwell_server == test_cromwell_url
        ), f"Cromwell server variable should be set to " \
           f"the specified server url : {test_cromwell_url}"
        reset_cromshellconfig(mock_data_path)

    def test_resolve_cromwell_config_server_address_provided_workflow_id_present(
            self, mock_data_path
    ):
        mock_workflow_id_present = "d689adec-c600-4e4b-be37-4e30e65848c7"
        mock_cromwell_url = "https://cromwell-v45.dsde-methods.broadinstitute.org"
        reset_cromshellconfig(mock_data_path)

        # Test when workflow id only is given to function and id
        # is present in submission file.
        cromshellconfig.resolve_cromwell_config_server_address(
            workflow_id=mock_workflow_id_present
        )
        assert (
                cromshellconfig.cromwell_server == mock_cromwell_url
        ), f"Cromwell server variable should be set to {mock_cromwell_url}"
        reset_cromshellconfig(mock_data_path)

    def test_resolve_cromwell_config_server_address_provided_workflow_id_absent(
            self, mock_data_path
    ):
        mock_workflow_id_absent = "h634sdv-x687-8m5e-mx13-1o97e30848h8"
        default_cromwell_url = cromshellconfig.cromwell_server
        reset_cromshellconfig(mock_data_path)

        # Test when workflow id only is given to function and id
        # is NOT present in submission file.
        cromshellconfig.resolve_cromwell_config_server_address(
            workflow_id=mock_workflow_id_absent
        )
        assert (
                cromshellconfig.cromwell_server == default_cromwell_url
        ), f"Cromwell server variable should be set to {default_cromwell_url}"
        reset_cromshellconfig(mock_data_path)

    def test_resolve_cromwell_config_server_address_provided_workflow_id_and_server(
            self, mock_data_path
    ):
        test_cromwell_url = "https://cromwell-v1.dsde-methods.broadinstitute.org"
        mock_workflow_id_present = "d689adec-c600-4e4b-be37-4e30e65848c7"
        reset_cromshellconfig(mock_data_path)

        # Cromwell url parameter should supersede workflow id look up
        cromshellconfig.resolve_cromwell_config_server_address(
            server_user=test_cromwell_url, workflow_id=mock_workflow_id_present
        )
        assert (
                cromshellconfig.cromwell_server == test_cromwell_url
        ), f"Cromwell server variable should be set to {test_cromwell_url}"

    def test_config_dir(self):
        reload(cromshellconfig)
        assert cromshellconfig.config_dir is not None, "Config variable should be set"

        assert cromshellconfig.config_dir == os.path.join(
            Path.home(), ".cromshell"
        ), "Config file variable path should be in .cromshell"

        assert Path(
            cromshellconfig.config_dir
        ).exists(), "Config directory should exist "

    def test_submission_file(self):
        reload(cromshellconfig)
        assert (
                cromshellconfig.submission_file_path is not None
        ), "Submission file variable should be set "

        path_to_submission = os.path.join(
            Path.home(), ".cromshell", cromshellconfig.submission_file_name
        )
        assert (
                cromshellconfig.submission_file_path == path_to_submission
        ), f"Submission file path should be {path_to_submission} "

        assert Path(
            cromshellconfig.submission_file_path
        ).exists(), "Submission file should exist"

    def test_cromwell_server(self):
        reload(cromshellconfig)
        assert (
                cromshellconfig.cromwell_server is not None
        ), "Cromwell server should be set"

    def test__load_cromshell_config_options(self, mock_data_path):
        reload(cromshellconfig)
        cc__load_cromshell_config_file = getattr(
            cromshellconfig, "__load_cromshell_config_file"
        )
        returned_value = cc__load_cromshell_config_file(os.path.dirname(mock_data_path))

        assert returned_value is not None, "Variable should not be empty"
        assert type(returned_value) is dict, "Variable should be a dictionary"

    @pytest.fixture
    def mock_data_path(self):
        return os.path.join(os.path.dirname(__file__), "mock_data/")
