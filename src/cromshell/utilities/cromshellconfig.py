import logging
from pathlib import Path

LOGGER = logging.getLogger(__name__)


class CromshellConfig:
    """Setup Cromshell config details. Intended to be used as a singleton"""

    @classmethod
    def user_defined_slim_metadata_parameters(cls, slim_metadata_parameters_user):
        """Override Cromwell Slim Metadata Key From Command Line"""
        if slim_metadata_parameters_user:
            cls.slim_metadata_parameters = (
                slim_metadata_parameters_user
                + "&includeKey=subWorkflowMetadata&includeKey=subWorkflowId"
            )

    @classmethod
    def resolve_cromwell_config_server_address(cls, server_user=None, workflow_id=None):
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

        if server_user is None and workflow_id is None:
            LOGGER.info(
                "Workflow id and cromwell server not specified. Using default cromwell server"
            )
        elif server_user:
            cls.cromwell_server = server_user
            LOGGER.info(
                "Cromwell server URL was overridden by command line argument"
            )
        else:
            with open(cls.submission_file) as f:
                column = None
                for line in f:
                    if workflow_id in line:
                        column = line.split()
                if column:
                    LOGGER.info("Found workflow id in submission file.")
                    cls.cromwell_server = column[1]
                    LOGGER.info(
                        "Cromwell server set to matching workflow id in submission file."
                    )
                else:
                    LOGGER.info(
                        "Unable to find workflow id in submission file. Using default"
                    )
            LOGGER.info(f"WorkflowID: {workflow_id}")
        LOGGER.info(f"Server: {cls.cromwell_server}")

    @classmethod
    def user_defined_show_logo(cls, verbosity):
        """Boolean for Displaying Turtle Logo"""

        if verbosity is None or verbosity < logging.CRITICAL:
            cls.is_verbose = True
        else:
            cls.is_verbose = False

    @staticmethod
    def __get_config_dir():
        """Get Path To Cromshell Hidden Directory"""

        config_path = str(Path.home()) + "/.cromshell"
        Path.mkdir(Path(config_path), exist_ok=True)
        return config_path

    @staticmethod
    def __get_submission_file(config_dir):
        """Get File Path To Cromshell Submission File"""

        submission_file = f"{config_dir}/all.workflow.database.tsv"
        if not Path.exists(Path(submission_file)):
            Path.touch(Path(submission_file))
            submission_header = (
                f"DATE\tCROMWELL_SERVER\tRUN_ID\tWDL_NAME\tSTATUS\tALIAS"
            )
            with Path(submission_file).open('w') as f:
                f.write(submission_header)
        return submission_file

    @staticmethod
    def __get_cromwell_server(config_dir):
        """Get Cromshell Server URL from Configuration File"""

        cromwell_server_path = f"{config_dir}/cromwell_server.config"
        if Path(cromwell_server_path).exists():
            with Path(cromwell_server_path).open() as f:
                cromwell_server = f.readline().strip()
            LOGGER.info("Setting cromwell server to cromwell url from config file.")
            LOGGER.info(cromwell_server)
            return cromwell_server
        else:
            LOGGER.error("Could not find cromwell_server.config")
            LOGGER.info("Creating file %s", cromwell_server_path)
            Path(cromwell_server_path).touch()
            LOGGER.error(
                "Please add a Cromwell server URL to file %s", cromwell_server_path
            )
            raise Exception(f"Please add a Cromwell server URL to file {cromwell_server_path}")

    # Set Cromshell Configuration Default Values
    metadata_parameters = "excludeKey=submittedFiles&expandSubWorkflows=true"
    config_dir = __get_config_dir.__func__()
    submission_file = __get_submission_file.__func__(config_dir)
    cromwell_server = __get_cromwell_server.__func__(config_dir)
    slim_metadata_parameters = (
        "=includeKey=id&includeKey=executionStatus&includeKey=backendStatus&includeKey"
        "=status&includeKey=callRoot&expandSubWorkflows=true&includeKey"
        "=subWorkflowMetadata&includeKey=subWorkflowId"
    )
    api_string = "/api/workflows/v1/"
