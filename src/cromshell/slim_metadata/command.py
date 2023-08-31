import logging

import click

from cromshell.metadata import command as metadata_command
from cromshell.utilities import command_setup_utils, io_utils

LOGGER = logging.getLogger(__name__)


@click.command(name="slim-metadata")
@click.argument("workflow_id")
@click.option(
    "-k",
    "--keys",
    help="Use keys to get a subset of the metadata for a workflow. "
    "Separate multiple keys by comma (e.g. '-k id[,status,...]').",
)
@click.option(
    "-des",
    "--dont-expand-subworkflows",
    is_flag=True,
    default=False,
    help="Do not expand subworkflow info in metadata",
)
@click.option(
    "-x",
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
    keys: list,
    dont_expand_subworkflows: bool,
    exclude_keys: bool,
):
    """Get a subset of the workflow metadata."""

    LOGGER.info("slim-metadata")

    # If no keys were provided then set key_param to empty else
    # strip trailing comma from keys and split keys by comma
    key_param = [] if not keys else str(keys).strip(",").split(",")

    command_setup_utils.resolve_workflow_id_and_server(
        workflow_id=workflow_id, cromshell_config=config
    )

    # Resolve and get metadata keys from cli, config file, or config default
    metadata_parameter = resolve_and_return_metadata_keys(
        cli_key=key_param,
        cromshell_config_options=config.cromshell_config_options,
        config_slim_metadata_default_param=config.SLIM_METADATA_DEFAULT_KEYS,
    )

    key_action = "include" if not exclude_keys else "exclude"
    LOGGER.info("Metadata keys set to %s: %s", key_action, metadata_parameter)

    workflow_metadata_json = metadata_command.format_metadata_params_and_get_metadata(
        config=config,
        metadata_param=metadata_parameter,
        exclude_keys=exclude_keys,
        dont_expand_subworkflows=dont_expand_subworkflows,
    )

    io_utils.pretty_print_json(format_json=workflow_metadata_json)

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
        LOGGER.info("No custom metadata keys were found in cli or config file.")
        # The default metadata key needs to
        return config_slim_metadata_default_param
