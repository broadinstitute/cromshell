import logging

import click
import requests

from cromshell.utilities import cromshellconfig, http_utils, io_utils

LOGGER = logging.getLogger(__name__)


@click.command(name="metadata")
@click.argument("workflow_id")
@click.option(
    "--key",
    "-k",
    multiple=True,
    help="Use keys to get a subset of the metadata for a workflow. Multiple keys "
    "can be set by add option name before adding key (e.g. '-k id -k status ...')",
)
@click.option(
    "-nes",
    "--not_expand_subworkflow",
    is_flag=True,
    default=True,
    help="Do not expand subworkflow info in metadata",
)
@click.option(
    "-e",
    "--exclude_keys",
    is_flag=True,
    show_default=True,
    default=False,
    help="Toggle to either include or exclude keys that are specified "
         "by the --keys option or in the cromshell config JSON.",
)
@click.pass_obj
def main(
        config,
        workflow_id: str,
        key: list,
        not_expand_subworkflow: bool,
        exclude_keys: bool
):
    """Get the full metadata of a workflow."""

    LOGGER.info("metadata")

    # Overrides the default cromwell url set in the cromshell config file or
    # command line argument if the workflow id is found in the submission file.
    cromshellconfig.resolve_cromwell_config_server_address(workflow_id=workflow_id)

    config.cromwell_api_workflow_id = f"{config.cromwell_api}/{workflow_id}"

    # Check if Cromwell Server Backend works
    http_utils.assert_can_communicate_with_server(config)

    # Resolve and get metadata keys from cli, config file, or config default
    metadata_parameter, using_default_meta_param = resolve_and_return_metadata_keys(
        cli_key=key,
        cromshell_config_options=config.cromshell_config_options,
        config_metadata_param=config.METADATA_PARAMETERS,
    )

    LOGGER.info("Metadata keys set to: %s", metadata_parameter)

    # If default parameter is being used we'll want to set exclude_keys to True
    # because by default we want to exclude the submittedFiles Field
    if using_default_meta_param:
        exclude_keys = True

    # Combine keys and flags into a dictionary
    combined_metadata_parameter = combine_keys_and_flags(
        list_of_keys=metadata_parameter,
        exclude_keys=exclude_keys,
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


def resolve_and_return_metadata_keys(
    cli_key: list,
    cromshell_config_options: dict,
    config_metadata_param: dict,
) -> (list, bool):
    """Determines which metadata keys to use from cli, config file, and default
    parameters, then returns a string of the processed keys ready to be used
    in an api call. Also returns true if default parameter is being used else false."""

    # If keys is specified in cli then use this first
    if cli_key:
        LOGGER.info("Using metadata key(s) from command line options.")
        return cli_key, False

    # If metadata_keys is specified in cromshell config file then use it for keys
    elif "metadata_keys" in cromshell_config_options:
        LOGGER.info("Setting metadata key(s) from value in config file.")
        return cromshell_config_options["metadata_keys"], False

    # Return the default keys from config module constant
    else:
        LOGGER.info("No metadata keys were found in cli or config file.")
        # The default metadata key needs to
        return config_metadata_param["keys"], True


def combine_keys_and_flags(
        list_of_keys: list, exclude_keys: bool, not_expand_subworkflow: bool
) -> dict:
    """This functions organises a list of cromwell metadata keys and flags into a
     dictionary that can passed to requests library"""

    if not list_of_keys:
        LOGGER.error("Function combine_keys_and_flags was given an empty list.")
        raise ValueError("Function combine_keys_and_flags was given an empty list.")
    elif None in list_of_keys:
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
