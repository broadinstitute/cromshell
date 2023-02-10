import logging

import click
import requests

from cromshell.utilities import command_setup_utils, http_utils, io_utils, cromshellconfig

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

    command_setup_utils.resolve_workflow_id_and_server(
        workflow_id=workflow_id, cromshell_config=config
    )

    workflow_metadata_json = format_metadata_params_and_get_metadata(
        config=config,
        metadata_param=config.METADATA_KEYS_TO_OMIT,
        exclude_keys=True,
        dont_expand_subworkflows=dont_expand_subworkflows,
    )

    io_utils.pretty_print_json(format_json=workflow_metadata_json, add_color=True)

    return 0


def format_metadata_params(
    list_of_keys: list, exclude_keys: bool, expand_subworkflows: bool
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

        if expand_subworkflows:
            final_key["expandSubWorkflows"] = "true"

        return final_key


def get_workflow_metadata(
    meta_params: dict,
    api_workflow_id: str,
    timeout: int,
    verify_certs: bool,
    headers: map,
) -> dict:
    """Uses requests to get the metadata or sub-metadata of a workflow
    from the cromwell server and returns it as a dictionary."""

    requests_out = requests.get(
        f"{api_workflow_id}/metadata",
        params=meta_params,
        timeout=timeout,
        verify=verify_certs,
        headers=headers,
    )

    http_utils.check_http_request_status_code(
        short_error_message="Failed to get metadata", response=requests_out
    )

    return requests_out.json()


def format_metadata_params_and_get_metadata(
    config: object,
    exclude_keys: bool,
    metadata_param: list[str] = cromshellconfig.METADATA_KEYS_TO_OMIT,
    dont_expand_subworkflows: bool = False
) -> dict:
    """
    Format metadata parameters and obtains metadata from cromwell server

    :param config: cromshell config object
    :param exclude_keys: Whether to the given keys should be excluded from the metadata
    :param metadata_param: Keys present in the workflow metadata
    :param dont_expand_subworkflows: Whether to the included subworkflow metadata
    :return:
    """

    # Combine keys and flags into a dictionary
    formatted_metadata_parameter = format_metadata_params(
        list_of_keys=metadata_param,
        exclude_keys=exclude_keys,
        expand_subworkflows=not dont_expand_subworkflows,  # Invert variable
    )

    # Request workflow metadata
    return get_workflow_metadata(
        meta_params=formatted_metadata_parameter,
        api_workflow_id=config.cromwell_api_workflow_id,
        timeout=config.requests_connect_timeout,
        verify_certs=config.requests_verify_certs,
        headers=http_utils.generate_headers(config),
    )
