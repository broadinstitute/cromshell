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

    # Overrides the default cromwell url set in the cromshell config file or
    # command line argument if the workflow id is found in the submission file.
    cromshellconfig.resolve_cromwell_config_server_address(workflow_id=workflow_id)

    # Check if Cromwell Server Backend works
    http_utils.assert_can_communicate_with_server(config)

    # Request workflow metadata
    raw_workflow_metadata = get_workflow_metadata(
            meta_par=config.METADATA_PARAMETERS,
            slim_meta=slim_metadata,
            api_workflow_id=config.cromwell_api_workflow_id,
            timeout=config.requests_connect_timeout,
            verify_certs=config.requests_verify_certs,
        )

    workflow_metadata_json = raw_workflow_metadata.content.decode("utf-8")

    io_utils.pretty_print_json(workflow_metadata_json)

    return 0


def get_workflow_metadata(
    meta_par: str,
    slim_meta: str,
    api_workflow_id: str,
    timeout: int,
    verify_certs: bool,
):
    """Use requests to get the metadata or sub-metadata of
    a workflow from the cromwell server."""

    # If set, use slim_meta as metadata parameter to be used in api requests
    if slim_meta:
        meta_par = slim_meta

    return requests.get(
        f"{api_workflow_id}/metadata?{meta_par}",
        timeout=timeout,
        verify=verify_certs
    )


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
