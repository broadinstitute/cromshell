import logging

import click
import requests

from cromshell.utilities import cromshellconfig, http_utils, io_utils

LOGGER = logging.getLogger(__name__)


@click.command(name="metadata")
@click.argument("workflow_id")
@click.option(
    "-nes",
    "--not_expand_subworkflow",
    is_flag=True,
    default=True,
    help="Do not expand subworkflow info in metadata",
)
@click.pass_obj
def main(config, workflow_id: str, not_expand_subworkflow: bool):
    """Get the full metadata of a workflow."""

    LOGGER.info("metadata")

    # Overrides the default cromwell url set in the cromshell config file or
    # command line argument if the workflow id is found in the submission file.
    cromshellconfig.resolve_cromwell_config_server_address(workflow_id=workflow_id)

    config.cromwell_api_workflow_id = f"{config.cromwell_api}/{workflow_id}"

    # Check if Cromwell Server Backend works
    http_utils.assert_can_communicate_with_server(config)

    # Combine keys and flags into a dictionary
    combined_metadata_parameter = combine_keys_and_flags(
        list_of_keys=config.METADATA_PARAMETERS,
        exclude_keys=True,
        not_expand_subworkflow=not_expand_subworkflow,
    )

    # Request workflow metadata
    workflow_metadata_json = get_workflow_metadata(
        meta_params=combined_metadata_parameter,
        api_workflow_id=config.cromwell_api_workflow_id,
        timeout=config.requests_connect_timeout,
        verify_certs=config.requests_verify_certs,
    )

    io_utils.pretty_print_json(workflow_metadata_json, add_color=True)

    return 0


def combine_keys_and_flags(
        list_of_keys: list, exclude_keys: bool, not_expand_subworkflow: bool
) -> dict:
    """This functions organises a list of cromwell metadata keys and flags into a
     dictionary that can passed to requests library"""

    if not list_of_keys:
        LOGGER.error("Function combine_keys_and_flags was given an empty list.")
        raise ValueError("Function combine_keys_and_flags was given an empty list.")
    elif "" in list_of_keys:
        LOGGER.error(
            "Function combine_keys_and_flags was given a list with empty element."
        )
        raise ValueError(
            "Function combine_keys_and_flags was given a list with empty element."
        )
    else:
        # Determines whether the list of keys will be used to exclude or
        # include fields in the metadata.
        key_action = "excludeKey" if exclude_keys else "includeKey"

        final_key = {key_action: list_of_keys}

        if not_expand_subworkflow:
            final_key["expandSubWorkflows"] = "true"

        return final_key


def get_workflow_metadata(
    meta_params: dict,
    api_workflow_id: str,
    timeout: int,
    verify_certs: bool,
) -> str:
    """Use requests to get the metadata or sub-metadata of
    a workflow from the cromwell server."""

    requests_out = requests.get(
        f"{api_workflow_id}/metadata",
        params=meta_params,
        timeout=timeout,
        verify=verify_certs,
    )

    http_utils.check_http_request_status_code(
        short_error_message="Failed to get metadata", response=requests_out
    )

    return requests_out.json()
