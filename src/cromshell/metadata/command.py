import logging

import click
import requests

from cromshell.utilities import cromshellconfig, http_utils, io_utils

LOGGER = logging.getLogger(__name__)


@click.command(name="metadata")
@click.argument("workflow_id")
# Setting is_flag=False, flag_value=value tells Click that the
# option can still be passed a value, but if only the flag is
# given the flag_value is used.
@click.option(
    "--slim_metadata",
    is_flag=False,
    flag_value="=includeKey=id&includeKey=executionStatus&includeKey=backendStatus"
    "&includeKey=status&includeKey=callRoot&expandSubWorkflows=true&includeKey"
    "=subWorkflowMetadata&includeKey=subWorkflowId",
    help="Get a subset of the metadata for a workflow",
)
@click.pass_obj
def main(config, workflow_id, slim_metadata):
    """Get the full metadata of a workflow."""

    LOGGER.info("metadata")

    config.cromwell_api_workflow_id = f"{config.cromwell_api}/{workflow_id}"

    # Set cromwell server using submission file. Running the function below with
    # passing only the workflow id overrides the default cromwell url set in the
    # cromshell config file, command line argument, and environment. This takes
    # place only if the workflow id is found in the submission file.
    cromshellconfig.resolve_cromwell_config_server_address(workflow_id=workflow_id)

    # Check if Cromwell Server Backend works
    http_utils.assert_can_communicate_with_server(config)

    # Request workflow status
    if slim_metadata:
        request_out = requests.get(
            f"{config.cromwell_api_workflow_id}/metadata?{slim_metadata}",
            timeout=config.requests_connect_timeout,
            verify=config.requests_verify_certs,
        )
    else:
        request_out = requests.get(
            f"{config.cromwell_api_workflow_id}/metadata?{config.METADATA_PARAMETERS}",
            timeout=config.requests_connect_timeout,
            verify=config.requests_verify_certs,
        )

    requested_metadata_json = request_out.content.decode("utf-8")

    io_utils.pretty_print_json(requested_metadata_json)

    return 0
