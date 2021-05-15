import logging

import click
import requests

from cromshell.utilities import cromshellconfig, http_utils, io_utils

LOGGER = logging.getLogger(__name__)


@click.command(name="metadata")
@click.argument("workflow_id")
# If multiple is set to True then the argument is accepts multiple times.
@click.option(
    "--key",
    "-k",
    default=[
        "id",
        "executionStatus",
        "backendStatus",
        "status",
        "callRoot&expandSubWorkflows=true",
        "subWorkflowMetadata",
        "subWorkflowId",
    ],
    show_default=True,
    multiple=True,
    help="Use keys to get a subset of the metadata for a workflow. Will use default"
         "keys if key is not provided in the command line option. Add option name"
         "before adding key (e.g. '-k id -k status ...')",
)
@click.pass_obj
def main(config, workflow_id: str, key: list):
    """Get the full metadata of a workflow."""

    LOGGER.info("metadata")

    config.cromwell_api_workflow_id = f"{config.cromwell_api}/{workflow_id}"

    # Overrides the default cromwell url set in the cromshell config file or
    # command line argument if the workflow id is found in the submission file.
    cromshellconfig.resolve_cromwell_config_server_address(workflow_id=workflow_id)

    # Check if Cromwell Server Backend works
    http_utils.assert_can_communicate_with_server(config)

    # If set, create a key string from list of key to use
    # as metadata parameter for api requests
    metadata_parameter = process_keys(key) if key else config.METADATA_PARAMETERS

    # Request workflow metadata
    workflow_metadata_json = get_workflow_metadata(
        meta_par=metadata_parameter,
        api_workflow_id=config.cromwell_api_workflow_id,
        timeout=config.requests_connect_timeout,
        verify_certs=config.requests_verify_certs,
    )

    io_utils.pretty_print_json(workflow_metadata_json)

    return 0


def process_keys(list_of_keys: list) -> str:
    final_key = ""
    for key in list_of_keys:

        # If string of key is empty add an '=' to begin the string,
        # else add '&' to prep it for the key that will be added.
        final_key += "&" if final_key else "="

        # Append key to string of key
        final_key += f"includeKey={key}"

    return final_key


def get_workflow_metadata(
    meta_par: str,
    api_workflow_id: str,
    timeout: int,
    verify_certs: bool,
) -> str:
    """Use requests to get the metadata or sub-metadata of
    a workflow from the cromwell server."""

    raw_workflow_metadata = requests.get(
        f"{api_workflow_id}/metadata?{meta_par}", timeout=timeout, verify=verify_certs
    )

    return raw_workflow_metadata.content.decode("utf-8")
