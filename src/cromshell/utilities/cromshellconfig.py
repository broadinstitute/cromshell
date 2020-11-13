import logging
import json
from pathlib import Path
import csv

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
    global submission_file

    if server_user is None and workflow_id is None:
        LOGGER.info(
            "Workflow id and cromwell server not specified. Using default cromwell "
            "server "
        )
        LOGGER.info(f"Server: {cromwell_server}")
    elif server_user:
        cromwell_server = server_user
        LOGGER.info(
            "Cromwell server URL was overridden by command line argument"
        )
        LOGGER.info(f"Server: {cromwell_server}")
    else:
        with open(submission_file, 'r') as csv_file:
            reader = csv.DictReader(csv_file, delimiter="\t")
            for row in reader:
                if row["RUN_ID"] == workflow_id:
                    LOGGER.info("Found workflow id in submission file.")
                    cromwell_server = row["CROMWELL_SERVER"]
                    LOGGER.info(
                        "Cromwell server set to matching workflow id in submission "
                        "file. "
                    )
                    LOGGER.info(f"WorkflowID: {workflow_id}")
                    LOGGER.info(f"Server: {cromwell_server}")
                    break




def __get_config_dir():
    """Get Path To Cromshell Hidden Directory"""

    config_path = os.path.join(Path.home(), ".cromshell")
    Path.mkdir(Path(config_path), exist_ok=True)
    return config_path


def __get_submission_file(config_directory):
    """Get File Path To Cromshell Submission File"""

    submission_file_path = f"{config_directory}/all.workflow.database.tsv"
    if not Path.exists(Path(submission_file_path)):
        Path.touch(Path(submission_file_path))
        submission_header = (
            f"DATE\tCROMWELL_SERVER\tRUN_ID\tWDL_NAME\tSTATUS\tALIAS"
        )
        with Path(submission_file_path).open('w') as f:
            f.write(submission_header)
    return submission_file_path


def __load_cromshell_config_file(config_directory):
    """Load options from Cromshell Config File to dictionary"""

    cromshell_config_file = f"{config_directory}/cromshell_config.json"
    if not Path.exists(Path(cromshell_config_file)):
        LOGGER.error(f"Cromshell config file {cromshell_config_file} was not found")
        LOGGER.error(f"Please create {cromshell_config_file}")
        raise Exception(f"Cromshell config file {cromshell_config_file} was not found")

    with open(cromshell_config_file, 'r') as f:
        config_options = json.loads(f.read())

    return config_options


def __get_cromwell_server():
    """Get Cromshell Server URL from configuration options"""

    if not cromshell_config_options['cromwell_server']:
        raise Exception(f'Cromshell config file is missing "cromwell_server"')

    LOGGER.info("Setting cromwell server to cromwell url from config file.") # Why doesn't this get printed in the stdout?
    LOGGER.info(cromshell_config_options['cromwell_server'])

    return cromshell_config_options['cromwell_server']


# Get and Set Cromshell Configuration Default Values
config_dir = __get_config_dir()
submission_file = __get_submission_file(config_dir)
cromshell_config_options = __load_cromshell_config_file(config_dir)
cromwell_server = __get_cromwell_server()
