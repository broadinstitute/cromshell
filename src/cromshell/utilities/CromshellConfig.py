import logging
import sys
from pathlib import Path


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
    def override_cromwell_config_server(cls, server_user=None, workflow_id=None):
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
            cls.LOGGER.info(
                "Workflow id and cromwell server not specified. Using default"
            )
        elif server_user:
            cls.cromwell_server = server_user
            CromshellConfig.LOGGER.info(
                "Cromwell server set to the provided in cli or environment argument."
            )
            CromshellConfig.LOGGER.info(cls.cromwell_server)
        else:
            with open(cls.submission_file) as f:
                column = None
                for line in f:
                    if workflow_id in line:
                        column = line.split()
                if column:
                    cls.LOGGER.info("Found workflow id in submission file.")
                    cls.cromwell_server = column[1]
                    CromshellConfig.LOGGER.info(
                        "Cromwell server set to matching workflow id in submission file."
                    )
                    CromshellConfig.LOGGER.info(cls.cromwell_server)
                else:
                    cls.LOGGER.info(
                        "Unable to find workflow id in submission file. Using default"
                    )

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

        submission_file = "{}/all.workflow.database.tsv".format(config_dir)
        if not Path.exists(Path(submission_file)):
            Path.touch(Path(submission_file))
            submission_header = (
                "DATE{0}CROMWELL_SERVER{0}RUN_ID{0}WDL_NAME{0}STATUS{0}ALIAS".format(
                    "\t"
                )
            )
            with Path(submission_file).open() as f:
                f.write(submission_header)
        return submission_file

    @staticmethod
    def __get_cromwell_server(config_dir):
        """Get Cromshell Server URL from Configuration File"""

        cromwell_server_path = "{}/cromwell_server.config".format(config_dir)
        if Path.exists(Path(cromwell_server_path)):
            with Path(cromwell_server_path).open() as f:
                cromwell_server = f.readline().strip()
            return cromwell_server
            CromshellConfig.LOGGER.info(
                "Setting cromwell server to cromwell url from config file."
            )
            CromshellConfig.LOGGER.info(cromwell_server)
        else:
            CromshellConfig.LOGGER.error("Could not find cromwell_server.config")
            CromshellConfig.LOGGER.info("Creating file %s", cromwell_server_path)
            Path.touch(Path(cromwell_server_path))
            CromshellConfig.LOGGER.error(
                "Please add a Cromwell server URL to file %s", cromwell_server_path
            )
            sys.exit()

    LOGGER = logging.getLogger(__name__)

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
