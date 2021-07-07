import logging

import click
import requests

from cromshell.utilities import cromshellconfig, http_utils, io_utils

LOGGER = logging.getLogger(__name__)


@click.command(name="metadata")
@click.argument("workflow_id")
@click.option(
    "-des",
    "--dont-expand-subworkflows",
    is_flag=True,
    default=False,
    help="Do not expand subworkflow info in metadata",
)
@click.pass_obj
def main(config, workflow_id: str, dont_expand_subworkflows: bool):
    """Get the full metadata of a workflow."""

    LOGGER.info("metadata")

    check_cromwell_server(config=config, workflow_id=workflow_id)

    obtain_and_print_metadata(
        config=config,
        metadata_param=config.METADATA_KEYS_TO_OMIT,
        exclude_keys=True,
        dont_expand_subworkflows=dont_expand_subworkflows,
    )

    return 0


def check_cromwell_server(config, workflow_id):
    """Checks for an associated cromwell server for the workflow_id
    and checks connection with the cromwell server"""

    # Overrides the default cromwell url set in the cromshell config file or
    # command line argument if the workflow id is found in the submission file.
    cromshellconfig.resolve_cromwell_config_server_address(workflow_id=workflow_id)

    config.cromwell_api_workflow_id = f"{config.cromwell_api}/{workflow_id}"

    # Check if Cromwell Server Backend works
    http_utils.assert_can_communicate_with_server(config)


def format_metadata_params(
    list_of_keys: list, exclude_keys: bool, dont_expand_subworkflows: bool
) -> dict:
    """This functions organises a list of cromwell metadata keys and flags into a
    dictionary that can be passed to requests library"""

    if not list_of_keys:
        LOGGER.error("No keys provided when querying metadata parameter.")
        raise ValueError("No keys provided when querying metadata parameter.")
    elif "" in list_of_keys:
        LOGGER.error("One of the provided metadata keys is empty.")
        raise ValueError("One of the provided metadata keys is empty.")
    else:
        # Determines whether the list of keys will be used to exclude or
        # include fields in the metadata.
        key_action = "excludeKey" if exclude_keys else "includeKey"

        final_key = {key_action: list_of_keys}

        if dont_expand_subworkflows is False:
            final_key["expandSubWorkflows"] = "true"

        return final_key


def get_workflow_metadata(
    meta_params: dict,
    api_workflow_id: str,
    timeout: int,
    verify_certs: bool,
) -> str:
    """Uses requests to get the metadata or sub-metadata of a workflow
    from the cromwell server and returns a JSON formatted string."""

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


def obtain_and_print_metadata(
    config, metadata_param: list, exclude_keys: bool, dont_expand_subworkflows: bool
):
    """Format metadata parameters and obtains metadata from cromwell server"""

    # Combine keys and flags into a dictionary
    formatted_metadata_parameter = format_metadata_params(
        list_of_keys=metadata_param,
        exclude_keys=exclude_keys,
        dont_expand_subworkflows=dont_expand_subworkflows,
    )

    # Request workflow metadata
    workflow_metadata_json = get_workflow_metadata(
        meta_params=formatted_metadata_parameter,
        api_workflow_id=config.cromwell_api_workflow_id,
        timeout=config.requests_connect_timeout,
        verify_certs=config.requests_verify_certs,
    )

    io_utils.pretty_print_json(workflow_metadata_json, add_color=True)
