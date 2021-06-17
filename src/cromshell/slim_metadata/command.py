import logging

import click

from cromshell.utilities import cromshellconfig, http_utils, io_utils
from cromshell.metadata import command as metadata_command

LOGGER = logging.getLogger(__name__)


@click.command(name="slim-metadata")
@click.argument("workflow_id")
@click.option(
    "--key",
    "-k",
    multiple=True,
    help="Use keys to get a subset of the metadata for a workflow. Multiple keys "
    "can be set by add option name before adding key (e.g. '-k id -k status ...')",
)
@click.option(
    "-des"
    "--dont_expand_subworkflow",
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
        dont_expand_subworkflows: bool,
        exclude_keys: bool
):
    """Get a subset of the workflow metadata using default keys."""

    LOGGER.info("slim-metadata")

    # Overrides the default cromwell url set in the cromshell config file or
    # command line argument if the workflow id is found in the submission file.
    cromshellconfig.resolve_cromwell_config_server_address(workflow_id=workflow_id)

    config.cromwell_api_workflow_id = f"{config.cromwell_api}/{workflow_id}"

    # Check if Cromwell Server Backend works
    http_utils.assert_can_communicate_with_server(config)

    # Resolve and get metadata keys from cli, config file, or config default
    metadata_parameter = resolve_and_return_metadata_keys(
        cli_key=key,
        cromshell_config_options=config.cromshell_config_options,
        config_slim_metadata_default_param=config.SLIM_METADATA_PARAMETERS,
    )

    key_action = "include" if not exclude_keys else "exclude"
    LOGGER.info("Metadata keys set to %s: %s", key_action, metadata_parameter)

    formated_metadata_parameter = metadata_command.format_metadata_params(
        list_of_keys=metadata_parameter,
        exclude_keys=exclude_keys,
        expand_subworkflow=dont_expand_subworkflows,
    )

    # Request workflow metadata. Uses function from the metadata command.
    workflow_metadata_json = metadata_command.get_workflow_metadata(
        meta_params=formated_metadata_parameter,
        api_workflow_id=config.cromwell_api_workflow_id,
        timeout=config.requests_connect_timeout,
        verify_certs=config.requests_verify_certs,
    )

    io_utils.pretty_print_json(workflow_metadata_json, add_color=True)

    return 0


def resolve_and_return_metadata_keys(
    cli_key: list,
    cromshell_config_options: dict,
    config_slim_metadata_default_param: list,
) -> list:
    """Determines which metadata keys to use from cli, config file, and default
    parameters, then returns a string of the processed keys ready to be used
    in an api call. Also returns true if default parameter is being used else false."""

    # If keys is specified in cli then use this first
    if cli_key:
        LOGGER.info("Using metadata key(s) from command line options.")
        return cli_key

    # If metadata_keys is specified in cromshell config file then use it for keys
    elif "slim_metadata_keys" in cromshell_config_options:
        LOGGER.info("Setting metadata key(s) from value in config file.")
        return cromshell_config_options["slim_metadata_keys"]

    # Return the default keys from config module constant
    else:
        LOGGER.info("No metadata keys were found in cli or config file.")
        # The default metadata key needs to
        return config_slim_metadata_default_param
