import logging

import click

from cromshell.utilities import cromshellconfig, http_utils, io_utils
from cromshell.metadata import command as metadata_command

LOGGER = logging.getLogger(__name__)


@click.command(name="slim-metadata")
@click.argument("workflow_id")
@click.option(
    "--not_expand_subworkflow",
    is_flag=True,
    default=True,
    help="Do not expand subworkflow info in metadata",
)
@click.pass_obj
def main(config, workflow_id: str, not_expand_subworkflow: bool):
    """Get a subset of the workflow metadata using default keys."""

    LOGGER.info("slim-metadata")

    keys = [
        "id",
        "executionStatus",
        "backendStatus",
        "status",
        "callRoot",
    ]

    config.cromwell_api_workflow_id = f"{config.cromwell_api}/{workflow_id}"

    # Overrides the default cromwell url set in the cromshell config file or
    # command line argument if the workflow id is found in the submission file.
    cromshellconfig.resolve_cromwell_config_server_address(workflow_id=workflow_id)

    # Check if Cromwell Server Backend works
    http_utils.assert_can_communicate_with_server(config)

    # Request workflow metadata. Uses function from the metadata command.
    workflow_metadata_json = metadata_command.get_workflow_metadata(
        meta_par=metadata_command.process_keys_and_flags(
            keys, not_expand_subworkflow=not_expand_subworkflow
        ),
        api_workflow_id=config.cromwell_api_workflow_id,
        timeout=config.requests_connect_timeout,
        verify_certs=config.requests_verify_certs,
    )

    io_utils.pretty_print_json(workflow_metadata_json, add_color=True)

    return 0
