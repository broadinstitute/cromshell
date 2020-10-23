import logging
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
api_string = "/api/workflows/v1/"
is_verbose = True


def user_defined_slim_metadata_parameters(slim_metadata_parameters_user):
    """Override Cromwell Slim Metadata Key From Command Line"""
    if slim_metadata_parameters_user:
        global slim_metadata_parameters
        slim_metadata_parameters = (
                slim_metadata_parameters_user
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
    global submission_file

    if server_user is None and workflow_id is None:
        LOGGER.info(
            "Workflow id and cromwell server not specified. Using default cromwell server"
        )
    elif server_user:
        cromwell_server = server_user
        LOGGER.info(
            "Cromwell server URL was overridden by command line argument"
        )
    else:
        with open(submission_file) as f:
            column = None
            for line in f:
                if workflow_id in line:
                    column = line.split()
            if column:
                LOGGER.info("Found workflow id in submission file.")
                cromwell_server = column[1]
                LOGGER.info(
                    "Cromwell server set to matching workflow id in submission file."
                )
            else:
                LOGGER.info(
                    "Unable to find workflow id in submission file. Using default"
                )
        LOGGER.info(f"WorkflowID: {workflow_id}")
    LOGGER.info(f"Server: {cromwell_server}")


def user_defined_show_logo(verbosity):
    """Boolean for Displaying Turtle Logo"""

    global is_verbose

    if verbosity is None or verbosity < logging.CRITICAL:
        is_verbose = True
    else:
        is_verbose = False


def __get_config_dir():
    """Get Path To Cromshell Hidden Directory"""

    config_path = str(Path.home()) + "/.cromshell"
    Path.mkdir(Path(config_path), exist_ok=True)
    return config_path


def __get_submission_file(config_directory):
    """Get File Path To Cromshell Submission File"""

    submission_file = f"{config_directory}/all.workflow.database.tsv"
    if not Path.exists(Path(submission_file)):
        Path.touch(Path(submission_file))
        submission_header = (
            f"DATE\tCROMWELL_SERVER\tRUN_ID\tWDL_NAME\tSTATUS\tALIAS"
        )
        with Path(submission_file).open('w') as f:
            f.write(submission_header)
    return submission_file


def __get_cromwell_server(config_directory):
    """Get Cromshell Server URL from Configuration File"""

    cromwell_server_path = f"{config_directory}/cromwell_server.config"
    if Path(cromwell_server_path).exists():
        with Path(cromwell_server_path).open() as f:
            config_cromwell_server = f.readline().strip()
        LOGGER.info("Setting cromwell server to cromwell url from config file.")
        LOGGER.info(config_cromwell_server)
        return config_cromwell_server
    else:
        LOGGER.error("Could not find cromwell_server.config")
        LOGGER.info("Creating file %s", cromwell_server_path)
        Path(cromwell_server_path).touch()
        LOGGER.error(
            "Please add a Cromwell server URL to file %s", cromwell_server_path
        )
        raise Exception(f"Please add a Cromwell server URL to file {cromwell_server_path}")


# Get and Set Cromshell Configuration Default Values
config_dir = __get_config_dir()
submission_file = __get_submission_file(config_dir)
cromwell_server = __get_cromwell_server(config_dir)
