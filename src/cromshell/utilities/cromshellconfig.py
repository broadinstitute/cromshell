import csv
import json
import logging
import os
from enum import Enum
from pathlib import Path

LOGGER = logging.getLogger(__name__)

"""Setup Cromshell config details. Intended to be used as a singleton"""

# Set Cromshell Configuration Default Values
metadata_parameters = "excludeKey=submittedFiles&expandSubWorkflows=true"
slim_metadata_parameters = (
    "=includeKey=id&includeKey=executionStatus&includeKey=backendStatus&includeKey"
    "=status&includeKey=callRoot&expandSubWorkflows=true&includeKey"
    "=subWorkflowMetadata&includeKey=subWorkflowId"
)
api_string = "/api/workflows/v1"
# Concatenate the cromwell url, api string, and workflow ID. Set in subcommand.
cromwell_api_workflow_id = None
cromwell_api = None
# Defaults for variables will be set after functions have been defined
config_dir = None
SUBMISSION_FILE_NAME = "all.workflow.database.tsv"
CROMSHELL_CONFIG_FILE_NAME = "cromshell_config.json"
submission_file_path = None
cromshell_config_options = None
cromwell_server = None


class WorkflowStatuses(Enum):
    Failed = ["Failed", "fail"]
    Aborted = ["Aborted", "abort"]
    Running = ["Running"]
    Succeeded = ["Succeeded"]
    DOOMED = ["DOOMED"]


def override_slim_metadata_parameters(slim_metadata_param):
    """Override Cromwell Slim Metadata Key From Command Line"""

    global slim_metadata_parameters

    if slim_metadata_param:
        slim_metadata_parameters = (
            slim_metadata_param
            + "&includeKey=subWorkflowMetadata&includeKey=subWorkflowId"
        )


def resolve_cromwell_config_server_address(server_user=None, workflow_id=None):
    """
    Override Cromwell Server From Command Line or Environment or Submission file

    This function allows users to override the cromwell server set in the
    cromshell config file using the command line options or environment
    variables. By default the server URL in the config file is used, however
    if an URL is specified in the command line or environment then this
    overrides the default. If a workflow Id is provided without a server URL
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
        LOGGER.info(f"Server: {cromwell_server}")
    elif server_user:
        cromwell_server = server_user
        LOGGER.info("Cromwell server URL was overridden by command line argument")
        LOGGER.info(f"Server: {cromwell_server}")
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
                    LOGGER.info(f"WorkflowID: {workflow_id}")
                    LOGGER.info(f"Server: {cromwell_server}")
                    id_in_file = True
                    break
            if not id_in_file:
                LOGGER.info(
                    "Workflow id was not found in submission file, using default "
                    "cromwell server."
                )


def __get_config_dir():
    """Get Path To Cromshell Hidden Directory"""

    config_path = os.path.join(Path.home(), ".cromshell")
    Path.mkdir(Path(config_path), exist_ok=True)
    return config_path


def __get_submission_file(config_directory, sub_file_name):
    """Get File Path To Cromshell Submission File"""

    sub_file_path = os.path.join(config_directory, sub_file_name)
    if not Path(sub_file_path).exists():
        Path(sub_file_path).touch()
        submission_header = f"DATE\tCROMWELL_SERVER\tRUN_ID\tWDL_NAME\tSTATUS\tALIAS"
        with Path(sub_file_path).open("w") as f:
            f.write(submission_header)
    return sub_file_path


def __load_cromshell_config_file(config_directory, config_file_name):
    """Load options from Cromshell Config File to dictionary"""
    # TODO: Add more config settings to validate user key and values

    cromshell_config_file = os.path.join(config_directory, config_file_name)
    if not Path(cromshell_config_file).exists():
        LOGGER.error(f"Cromshell config file {cromshell_config_file} was not found")
        LOGGER.error(f"Please create {cromshell_config_file}")
        raise Exception(f"Cromshell config file {cromshell_config_file} was not found")

    with open(cromshell_config_file, "r") as f:
        config_options = json.loads(f.read())

    return config_options


def __get_cromwell_server():
    """Get Cromshell Server URL from configuration options"""

    if not cromshell_config_options["cromwell_server"]:
        raise Exception(f'Cromshell config file is missing "cromwell_server"')

    LOGGER.info("Setting cromwell server to cromwell url from config file.")
    LOGGER.info(cromshell_config_options["cromwell_server"])

    return cromshell_config_options["cromwell_server"]


# Get and Set Cromshell Configuration Default Values
config_dir = __get_config_dir()
submission_file_path = __get_submission_file(config_dir, SUBMISSION_FILE_NAME)
cromshell_config_options = __load_cromshell_config_file(
    config_dir, CROMSHELL_CONFIG_FILE_NAME
)
cromwell_server = __get_cromwell_server()
cromwell_api = cromwell_server + api_string
