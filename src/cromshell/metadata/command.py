import json
import logging

import click
import requests

from cromshell.utilities import cromshellconfig, http_utils, io_utils

LOGGER = logging.getLogger(__name__)


@click.command(name="metadata")
@click.argument("workflow_id")
@click.option(
    "--slim_metadata_parameters",
    type=str,
    help="Get a subset of the metadata for a workflow",
)
@click.pass_obj
def main(config, workflow_id, slim_metadata_parameters):
    """Get the full metadata of a workflow."""

    LOGGER.info("metadata")

    config.cromwell_api_workflow_id = f"{config.cromwell_api}/{workflow_id}"

    cromshellconfig.override_slim_metadata_parameters(slim_metadata_parameters)

    # Set cromwell server using submission file. Running the function below with
    # passing only the workflow id overrides the default cromwell url set in the
    # cromshell config file, command line argument, and environment. This takes
    # place only if the workflow id is found in the submission file.
    cromshellconfig.resolve_cromwell_config_server_address(workflow_id=workflow_id)

    # Check if Cromwell Server Backend works
    http_utils.assert_can_communicate_with_server(config)

    # Request workflow status
    request_out = requests.get(
        f"{config.cromwell_api_workflow_id}/metadata?{config.METADATA_PARAMETERS}",
        timeout=config.requests_connect_timeout,
        verify=config.requests_verify_certs,
    )

    requested_metadata_json = request_out.content.decode("utf-8")

    io_utils.pretty_print_json(requested_metadata_json)

    return 0
