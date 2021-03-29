import logging
from sys import argv

import click

from cromshell.utilities import cromshellconfig
from .status import command as status

# Version number is automatically set via bumpversion.
# DO NOT MODIFY:
__version__ = "2.0.0"

# Create a logger for this module:
LOGGER = logging.getLogger(__name__)


@click.group(name="cromshell")
@click.option(
    "-q",
    "--quiet",
    "verbosity",
    flag_value=logging.CRITICAL + 10,
    help="Suppress all logging",
)
@click.option(
    "-v",
    "--verbose",
    "verbosity",
    flag_value=logging.DEBUG,
    help="More verbose logging",
)
@click.option(
    "--trace",
    "verbosity",
    flag_value=logging.NOTSET,
    help="Highest level logging for debugging",
)
@click.option(
    "--hide_logo",
    flag_value=True,
    help="Hide turtle logo",
)
@click.option(
    "--slim_metadata_parameters",
    type=str,
    help="Get a subset of the metadata for a workflow",
)
@click.option(
    "--cromwell_url",
    type=str,
    help="Specify Cromwell URL used",
)
@click.option(
    "--request_timeout",
    type=int,
    help="Specify the server connection timeout in seconds."
    "Must be an integer. Default is 5.",
)
@click.option(
    "--requests_skip_certs",
    flag_value=True,
    help="Stops cromshell from verifying TLS certificate of server. "
    "The use of verification is strongly advised as per ssl documentation. "
    "Use this flag only when communicating with internal cromwell servers.",
)
@click.pass_context
def main_entry(
    cromshell_config,
    verbosity,
    slim_metadata_parameters,
    hide_logo,
    cromwell_url,
    request_timeout,
    requests_skip_certs,
):
    # Set up our log verbosity
    from . import log  # pylint: disable=C0415

    log.configure_logging(verbosity)
    log.override_logo_display_setting(hide_logo)

    # Log our command-line and log level so we can have it in the log file:
    LOGGER.info("Invoked by: %s", " ".join(argv))
    LOGGER.info("Log level set to: %s", logging.getLevelName(logging.getLogger().level))

    # Create an object to hold all cromwell configurations
    cromshell_config.obj = cromshellconfig
    cromshellconfig.override_slim_metadata_parameters(slim_metadata_parameters)
    cromshellconfig.resolve_cromwell_config_server_address(server_user=cromwell_url)
    cromshellconfig.override_requests_cert_parameters(skip_certs=requests_skip_certs)
    cromshellconfig.resolve_requests_connect_timeout(timeout_cli=request_timeout)


@main_entry.command()
def version():
    """Print the version of cromshell"""
    LOGGER.info("cromshell %s", __version__)


# Update with new sub-commands:
main_entry.add_command(status.main)


if __name__ == "__main__":
    main_entry()  # pylint: disable=E1120
