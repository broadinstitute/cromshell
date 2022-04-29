import os
from importlib import reload
from pathlib import Path

import pytest

from cromshell.utilities import cromshellconfig


def reset_cromshellconfig(mock_data_path):
    reload(cromshellconfig)

    # Set the submission file path to mock data
    cromshellconfig.submission_file_path = os.path.join(
        mock_data_path, cromshellconfig.SUBMISSION_FILE_NAME
    )


class TestCromshellConfig:
    """Test the cromshell config functions and variables"""

    def test_resolve_cromwell_config_server_address_not_empty(self):
        reload(cromshellconfig)

        assert (
            cromshellconfig.cromwell_server is not None
        ), "Cromwell server variable should not be empty"

    def test_resolve_cromwell_config_server_address_provided_server_url(
        self, mock_data_path
    ):
        """Test when server url only is given to function."""

        reset_cromshellconfig(mock_data_path)
        test_cromwell_url = "https://cromwell-v1.dsde-methods.broadinstitute.org"

        # Test when server only is given to function
        cromshellconfig.resolve_cromwell_config_server_address(
            server_user=test_cromwell_url
        )
        assert cromshellconfig.cromwell_server == test_cromwell_url, (
            f"Cromwell server variable should be set to "
            f"the specified server url : {test_cromwell_url}"
        )

    def test_resolve_cromwell_config_server_address_provided_workflow_id_present(
        self, mock_data_path
    ):
        """Test when workflow id only is given to function and id
        is present in submission file."""

        reset_cromshellconfig(mock_data_path)
        mock_workflow_id_present = "d689adec-c600-4e4b-be37-4e30e65848c7"
        mock_cromwell_url = "https://cromwell-v45.dsde-methods.broadinstitute.org"

        cromshellconfig.resolve_cromwell_config_server_address(
            workflow_id=mock_workflow_id_present
        )
        assert (
            cromshellconfig.cromwell_server == mock_cromwell_url
        ), f"Cromwell server variable should be set to {mock_cromwell_url}"

    def test_resolve_cromwell_config_server_address_provided_workflow_id_absent(
        self, mock_data_path
    ):
        """Test when workflow id only is given to function and id
        is NOT present in submission file."""

        reset_cromshellconfig(mock_data_path)
        mock_workflow_id_absent = "h634sdv-x687-8m5e-mx13-1o97e30848h8"
        default_cromwell_url = cromshellconfig.cromwell_server

        cromshellconfig.resolve_cromwell_config_server_address(
            workflow_id=mock_workflow_id_absent
        )
        assert (
            cromshellconfig.cromwell_server == default_cromwell_url
        ), f"Cromwell server variable should be set to {default_cromwell_url}"

    def test_resolve_cromwell_config_server_address_provided_workflow_id_and_server(
        self, mock_data_path
    ):
        """Cromwell url parameter should supersede workflow id look up"""

        reset_cromshellconfig(mock_data_path)
        test_cromwell_url = "https://cromwell-v1.dsde-methods.broadinstitute.org"
        mock_workflow_id_present = "d689adec-c600-4e4b-be37-4e30e65848c7"

        cromshellconfig.resolve_cromwell_config_server_address(
            server_user=test_cromwell_url, workflow_id=mock_workflow_id_present
        )
        assert (
            cromshellconfig.cromwell_server == test_cromwell_url
        ), f"Cromwell server variable should be set to {test_cromwell_url}"

    def test_config_dir(self):
        reload(cromshellconfig)
        assert cromshellconfig.config_dir is not None, "Config variable should be set"

        if os.environ.get("CROMSHELL_CONFIG"):
            path_to_hidden_folder = os.path.join(
                os.environ.get("CROMSHELL_CONFIG"), ".cromshell"
            )
        else:
            path_to_hidden_folder = os.path.join(Path.home(), ".cromshell")

        assert (
            cromshellconfig.config_dir == path_to_hidden_folder
        ), f"Config file variable path should be {path_to_hidden_folder} "

        assert Path(
            cromshellconfig.config_dir
        ).exists(), "Config directory should exist "

    def test_submission_file(self):
        reload(cromshellconfig)
        assert (
            cromshellconfig.submission_file_path is not None
        ), "Submission file variable should be set "

        if os.environ.get("CROMSHELL_CONFIG"):
            path_to_hidden_submission = os.path.join(
                os.environ.get("CROMSHELL_CONFIG"),
                ".cromshell",
                cromshellconfig.SUBMISSION_FILE_NAME,
            )
        else:
            path_to_hidden_submission = os.path.join(
                Path.home(), ".cromshell", cromshellconfig.SUBMISSION_FILE_NAME
            )

        assert (
            cromshellconfig.submission_file_path == path_to_hidden_submission
        ), f"Submission file path should be {path_to_hidden_submission}"

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
        returned_value = cc__load_cromshell_config_file(
            config_directory=os.path.dirname(mock_data_path),
            config_file_name=cromshellconfig.CROMSHELL_CONFIG_FILE_NAME,
            config_file_template=cromshellconfig.CROMSHELL_CONFIG_OPTIONS_TEMPLATE,
        )

        assert returned_value is not None, "Variable should not be empty"
        assert type(returned_value) is dict, "Variable should be a dictionary"

    def test_override_requests_cert_parameters(self):
        reload(cromshellconfig)

        assert (
            cromshellconfig.requests_verify_certs
        ), "By default certs should be verified"

        # Use the function below to disable cert verification.
        cromshellconfig.override_requests_cert_parameters(True)
        assert (
            not cromshellconfig.requests_verify_certs
        ), "Request certification should be overridden to be False"

    def test_resolve_requests_connect_timeout_default(self):
        reload(cromshellconfig)
        # CLI > Config File > Default

        assert (
            cromshellconfig.requests_connect_timeout is not None
        ), "By Default the requests timeout should be set to its default int"

        # Run function as if user did not provide timeout option in cli (None)
        timeout_from_command_line = None
        cromshellconfig.resolve_requests_connect_timeout(timeout_from_command_line)

        assert (
            cromshellconfig.requests_connect_timeout is not None
        ), "By Default the requests timeout should be set to its default int"

    def test_resolve_requests_connect_timeout_given_config_file_value(
        self, test_config_options_with_timeout
    ):
        reload(cromshellconfig)
        # CLI > Config File > Default

        # Provide a mock dictionary holding cromwell config options
        cromshellconfig.cromshell_config_options = test_config_options_with_timeout

        # Run function as if user did not provide timeout option in cli (None)
        timeout_from_command_line = None
        cromshellconfig.resolve_requests_connect_timeout(timeout_from_command_line)

        assert (
            cromshellconfig.requests_connect_timeout == 7
        ), "Requests timeout duration should be set to 7 sec"

    def test_resolve_requests_connect_timeout_given_cli_value(
        self, test_config_options_with_timeout
    ):
        reload(cromshellconfig)
        # CLI > Config File > Default

        timeout_from_command_line = 10

        # Provide a mock dictionary holding cromwell config options
        cromshellconfig.cromshell_config_options = test_config_options_with_timeout
        # Run function as if user provided timeout option in cli (10)
        cromshellconfig.resolve_requests_connect_timeout(timeout_from_command_line)

        assert (
            cromshellconfig.requests_connect_timeout == 10
        ), "Requests timeout duration should be set to 10 sec"

    def test_resolve_referer_header_url_default(self):
        reload(cromshellconfig)
        assert (
            cromshellconfig.referer_header_url is None
        ), "Default `referer_header_url` should be None"

    def test_resolve_referer_header_url_config(self, test_config_referer_header_url):
        reload(cromshellconfig)
        cromshellconfig.cromshell_config_options = test_config_referer_header_url
        referer_header_url_cli = None
        cromshellconfig.resolve_referer_header_url(referer_header_url_cli)

        assert (
            cromshellconfig.referer_header_url == "https://from_config.example.com"
        ), "Use config value in absence of CLI"

    def test_resolve_referer_header_url_cli(self, test_config_referer_header_url):
        reload(cromshellconfig)
        cromshellconfig.cromshell_config_options = test_config_referer_header_url
        referer_header_url_cli = "https://from_cli.example.com"
        cromshellconfig.resolve_referer_header_url(referer_header_url_cli)

        assert (
            cromshellconfig.referer_header_url == "https://from_cli.example.com"
        ), "CLI overrides config"

    def test_resolve_gcloud_token_email_default(self):
        reload(cromshellconfig)
        assert (
            cromshellconfig.gcloud_token_email is None
        ), "Default `gcloud_token_email` should be None"

    def test_resolve_gcloud_token_email_config(self, test_config_gcloud_token_email):
        reload(cromshellconfig)
        cromshellconfig.cromshell_config_options = test_config_gcloud_token_email
        gcloud_token_email_cli = None
        cromshellconfig.resolve_gcloud_token_email(gcloud_token_email_cli)

        assert (
            cromshellconfig.gcloud_token_email == "from_config@example.com"
        ), "Use config value in absence of CLI"

    def test_resolve_gcloud_token_email_cli(self, test_config_gcloud_token_email):
        reload(cromshellconfig)
        cromshellconfig.cromshell_config_options = test_config_gcloud_token_email
        gcloud_token_email_cli = "from_cli@example.com"
        cromshellconfig.resolve_referer_header_url(gcloud_token_email_cli)

        assert (
            cromshellconfig.referer_header_url == "from_cli@example.com"
        ), "CLI overrides config"

    @pytest.fixture
    def mock_data_path(self):
        return os.path.join(os.path.dirname(__file__), "mock_data/")

    @pytest.fixture
    def test_config_empty(self):
        return {}

    @pytest.fixture
    def test_config_gcloud_token_email(self):
        return {"gcloud_token_email": "from_config@example.com"}

    @pytest.fixture
    def test_config_referer_header_url(self):
        return {"referer_header_url": "https://from_config.example.com"}

    @pytest.fixture
    def test_config_options_with_timeout(self):
        config_demo = {
            "random_arg1": True,
            "requests_timeout": 7,
            "random_arg2": "Value",
        }
        return config_demo

    @pytest.fixture
    def test_config_options_without_timeout(self):
        config_demo = {"random_arg1": True, "random_arg2": "Value"}
        return config_demo
