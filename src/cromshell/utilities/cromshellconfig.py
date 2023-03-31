import csv
import json
import logging
import os
import sys
import warnings
from pathlib import Path
from typing import Dict, Union

import cromshell.utilities.config_options_file_utils as cofu
import cromshell.utilities.submissions_file_utils as submissions_file_utils

LOGGER = logging.getLogger(__name__)

"""Setup Cromshell config details. Intended to be used as a singleton"""

# Set Cromshell Configuration Default Values
METADATA_KEYS_TO_OMIT = ["submittedFiles"]
SLIM_METADATA_DEFAULT_KEYS = [
    "id",
    "executionStatus",
    "backendStatus",
    "status",
    "callRoot",
    "subWorkflowMetadata",
    "subWorkflowId",
]
CROMWELL_API_STRING = "/api/workflows/v1"
WOMTOOL_API_STRING = "/api/womtool/v1"
workflow_id = None
# Concatenate the cromwell url, api string, and workflow ID. Set in subcommand.
cromwell_api_workflow_id = None
# Defaults for variables will be set after functions have been defined
config_dir = None
SUBMISSION_FILE_NAME = "all.workflow.database.tsv"
CROMSHELL_CONFIG_FILE_NAME = "cromshell_config.json"
submission_file_path = None
cromshell_config_path = None
cromshell_config_options = None
cromwell_server = None
# Request defaults
requests_connect_timeout = 5
referer_header_url = None
gcloud_token_email = None
requests_verify_certs = True
color_output = None

CROMSHELL_CONFIG_OPTIONS_TEMPLATE = {
    "cromwell_server": "String",
    "requests_timeout": requests_connect_timeout,
}


def override_requests_cert_parameters(skip_certs: bool) -> None:
    """Override requests settings for certs verification"""

    global requests_verify_certs

    if skip_certs is True:
        requests_verify_certs = False
        LOGGER.warning("Skipping server TLS certificate verification.")
        # Since the log message regarding skipping certification is printed out
        # in the line above we will hide any future requests warning
        # about not verifying certs.
        warnings.filterwarnings(
            "ignore", message="Unverified HTTPS request is being made to"
        )


def resolve_cromwell_config_server_address(server_user=None, workflow_id=None) -> None:
    """
    Override Cromwell Server From Command Line or Environment or Submission file

    This function allows users to override the cromwell server set in the
    cromshell config file using the command line options or environment
    variables. By default, the server URL in the config file is used, however
    if a URL is specified in the command line or environment then this
    overrides the default. If a workflow ID is provided without a server URL
    then the server associated with a workflow id in the submission file
    overrides the default. If a workflow ID is provided but isn't found
    in the submission file then the default server is used.
    """

    global cromwell_server
    global submission_file_path

    if server_user is None and workflow_id is None:
        LOGGER.info(
            "Workflow id and cromwell server not specified. Using default cromwell "
            "server "
        )
        LOGGER.info("Server: %s", cromwell_server)
    elif server_user:
        cromwell_server = server_user
        LOGGER.info("Cromwell server URL was overridden by command line argument")
        LOGGER.info("Server: %s", cromwell_server)
    else:
        LOGGER.info(
            "Checking submission file for associated cromwell server with the provided "
            "workflow id."
        )

        with open(submission_file_path, "r") as csv_file:
            reader = csv.DictReader(csv_file, delimiter="\t")
            id_in_file = False
            for row in reader:
                if row["RUN_ID"] == workflow_id:
                    cromwell_server = row["CROMWELL_SERVER"]
                    LOGGER.info(
                        "Cromwell server set to matching workflow id in submission "
                        "file. "
                    )
                    LOGGER.info("WorkflowID: %s", workflow_id)
                    LOGGER.info("Server: %s", cromwell_server)
                    id_in_file = True
                    break
            if not id_in_file:
                LOGGER.info(
                    "Workflow id was not found in submission file, using default "
                    "cromwell server."
                )


def __get_config_dir() -> str:
    """Get Path To Cromshell Hidden Directory"""

    # If env CROMSHELL_CONFIG set then use for cromshell hidden dir else use home dir.
    if os.environ.get("CROMSHELL_CONFIG"):
        LOGGER.info(
            "Detected 'CROMSHELL_CONFIG' in environment, using {config_path} as "
            "cromshell hidden directory."
        )
        config_path = os.path.join(os.environ.get("CROMSHELL_CONFIG"), ".cromshell")

    else:
        config_path = os.path.join(Path.home(), ".cromshell")

    Path.mkdir(Path(config_path), exist_ok=True, parents=True)
    LOGGER.info(f"Cromshell config directory set to {config_path}.")

    return config_path


def __get_submission_file(config_directory: Path, sub_file_name: str) -> str:
    """
    Get File Path To Cromshell Submission File path. Creates new submission file
    if one does not already exist.
    :param config_directory: Path to cromshell config directory
    :param sub_file_name: Name of cromshell submission file
    :return: Path to cromshell submission file
    """

    sub_file_path = os.path.join(config_directory, sub_file_name)

    if not Path(sub_file_path).exists():
        Path(sub_file_path).touch()
        with Path(sub_file_path).open("w") as sub_file:
            dw = csv.DictWriter(
                sub_file,
                delimiter="\t",
                fieldnames=submissions_file_utils.WorkflowDatabaseColumns.get_submission_file_headers(),
            )
            dw.writeheader()
    return sub_file_path


def __load_cromshell_config_file(
    config_directory: str, config_file_name: str, config_file_template: dict
) -> Dict[str, Union[str, list, int, dict, float]]:
    """
    Load options from Cromshell Config File to dictionary.

    :param config_directory: Path to cromshell config directory
    :param config_file_name:
    :param config_file_template:
    :return:
    """

    cromshell_config_path = Path(os.path.join(config_directory, config_file_name))
    if not Path(cromshell_config_path).exists():
        LOGGER.info("Cromshell config file %s was not found", cromshell_config_path)
        LOGGER.info("Creating %s", cromshell_config_path)

        config_template = json.dumps(config_file_template, indent=2)

        Path(cromshell_config_path).touch()
        with Path(cromshell_config_path).open("w") as crom_config_file:
            crom_config_file.write(config_template)
        LOGGER.warning(
            "Please update the cromwell server in the following config file %s",
            cromshell_config_path,
        )

    cofu.validate_cromshell_config_options_file(
        config_options_file=cromshell_config_path
    )

    with open(cromshell_config_path, "r") as cromshell_config_file:
        config_options = json.loads(cromshell_config_file.read())

    return config_options


def __get_cromwell_server(config_options: dict) -> str:
    """Get Cromwell Server URL from configuration options"""

    if not config_options["cromwell_server"]:
        raise FileNotFoundError('Cromshell config file is missing "cromwell_server"')

    LOGGER.info("Setting cromwell server to cromwell url from config file.")
    LOGGER.info(config_options["cromwell_server"])

    return config_options["cromwell_server"]


def get_cromwell_api() -> str:
    """Return a string combining the cromwell server and the cromwell api string"""
    return f"{cromwell_server}{CROMWELL_API_STRING}"


def get_womtool_api() -> str:
    """Return a string combining the cromwell server and the womtool api string"""
    return f"{cromwell_server}{WOMTOOL_API_STRING}"


def get_local_folder_name() -> str:
    """Return a string combining the cromwell server without http/https"""
    return cromwell_server.replace("https://", "").replace("http://", "")


def resolve_requests_connect_timeout(timeout_cli: int) -> None:
    """Override the default request timeout duration.

    By default, the timeout duration is 5 sec, however
    if the option is specified in the cromshell config file or
    command line then this overrides the default.
    CLI > Config File > Default
    """

    global requests_connect_timeout

    # If timeout is specified in cli then use it to override default/config file
    if timeout_cli:
        LOGGER.info("Setting requests timeout from command line options.")
        LOGGER.info("Request Timeout value: %d sec", timeout_cli)
        requests_connect_timeout = timeout_cli

    # If timeout is specified in cromshell config file then use it to override default
    elif "requests_timeout" in cromshell_config_options:
        LOGGER.info("Setting requests timeout from value in config file.")
        LOGGER.info(
            "Request Timeout value: %d sec",
            cromshell_config_options["requests_timeout"],
        )
        # Set the requests_connect_timeout variable to timeout value in config file.
        requests_connect_timeout = cromshell_config_options["requests_timeout"]
    else:
        LOGGER.info("Using requests default timeout duration.")
        LOGGER.info("Request Timeout value: %d sec", requests_connect_timeout)


def resolve_referer_header_url(url: str) -> None:
    global referer_header_url

    if url:
        LOGGER.info(f"Will send referer header {url} from command line options.")
        referer_header_url = url
    elif "referer_header_url" in cromshell_config_options:
        config_url = cromshell_config_options["referer_header_url"]
        LOGGER.info(f"Will send referer header {config_url} from config.")
        referer_header_url = config_url
    else:
        LOGGER.info("No referer header URL set.")


def resolve_gcloud_token_email(email: str):
    global gcloud_token_email

    if email:
        LOGGER.info(
            f"Will send auth header with token for {email} from command line options."
        )
        gcloud_token_email = email
    elif "gcloud_token_email" in cromshell_config_options:
        config_gcloud_token_email = cromshell_config_options["gcloud_token_email"]
        LOGGER.info(
            f"Will send auth header with token for {config_gcloud_token_email} from config."
        )
        gcloud_token_email = config_gcloud_token_email
    else:
        LOGGER.info("Not sending auth header.")


def resolve_color_output(machine_readable: bool, colorful_output: bool) -> None:
    """Override the default color json output.
    Arg color: True or False"""
    global color_output

    if machine_readable and colorful_output:
        LOGGER.error("Cannot color json output and be machine readable.")
        LOGGER.error("Please choose one or the other Cromshell flags.")
        raise ValueError("Cannot color json output and be machine readable.")

    if machine_readable:
        LOGGER.debug("Will not color json output.")
        color_output = False
    elif colorful_output or sys.stdout.isatty():
        LOGGER.debug("Will color json output.")
        color_output = True
    else:
        LOGGER.debug("Will not color json output.")
        color_output = False


# Get and Set Cromshell Configuration Default Values
config_dir = __get_config_dir()
submission_file_path = __get_submission_file(
    config_directory=config_dir, sub_file_name=SUBMISSION_FILE_NAME
)
# TODO: Validate cromshell_config_options keys
cromshell_config_options = __load_cromshell_config_file(
    config_directory=config_dir,
    config_file_name=CROMSHELL_CONFIG_FILE_NAME,
    config_file_template=CROMSHELL_CONFIG_OPTIONS_TEMPLATE,
)
cromwell_server = __get_cromwell_server(cromshell_config_options)
cromshell_config_path: Path = Path(os.path.join(config_dir, CROMSHELL_CONFIG_FILE_NAME))
