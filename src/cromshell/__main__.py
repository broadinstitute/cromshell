import logging
from sys import argv

import click

from cromshell.utilities import cromshellconfig
from cromshell.utilities.submissions_file_utils import update_submission_db_format

from .abort import command as abort
from .alias import command as alias
from .cost import command as cost
from .counts import command as counts
from .list import command as list
from .list_outputs import command as list_outputs
from .logs import command as logs
from .metadata import command as metadata
from .slim_metadata import command as slim_metadata
from .status import command as status
from .submit import command as submit
from .timing import command as timing
from .update_server import command as update_server
from .validate import command as validate

# Version number is automatically set via bumpversion.
# DO NOT MODIFY:
__version__ = "2.1.1"

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
    "--info",
    "verbosity",
    flag_value=logging.INFO,
    help="Show logging",
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
    "--no_turtle",
    "--I_hate_turtles",
    flag_value=True,
    help="Hide turtle logo",
)
@click.option(
    "-cu",
    "--cromwell_url",
    type=str,
    help="Specify Cromwell URL used. Example: 'http://65.61.654.8:8000'.",
)
@click.option(
    "-t",
    "--requests_timeout",
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
@click.option(
    "--gcloud_token_email",
    type=str,
    help="Call `gcloud auth print-access-token` with this email and add the token as an auth header to requests.",
)
@click.option(
    "--referer_header_url",
    type=str,
    help="For servers that require a referer, supply this URL in the `Referer:` header.",
)
@click.option(
    "-mc",
    "--machine_processable",
    "machine_processable",
    flag_value=True,
    help="Avoids the use of color and other human readable formatting for output.",
)
@click.option(
    "-co",
    "--colorful_output",
    "colorful_output",
    flag_value=True,
    help="Uses color and other human readable formatting for output when possible.",
)
@click.pass_context
def main_entry(
    cromshell_config,
    verbosity,
    no_turtle,
    cromwell_url,
    requests_timeout,
    requests_skip_certs,
    gcloud_token_email,
    referer_header_url,
    machine_processable,
    colorful_output,
):
    """
    Cromshell is a script for submitting workflows to a
    cromwell server and monitoring / querying their results.\n
    Notes:\n
        - A hidden folder will be created on initial run. The hidden folder
    (.../.cromshell) will be placed in users home directory but can be overridden
    by setting environment variable 'CROMSHELL_CONFIG'.
    """
    # Set up our log verbosity
    from . import log  # pylint: disable=C0415

    log.configure_logging(verbosity)
    log.override_logo_display_setting(no_turtle)

    # Log our command-line and log level, so we can have it in the log file:
    LOGGER.info("Invoked by: %s", " ".join(argv))
    LOGGER.info("Log level set to: %s", logging.getLevelName(logging.getLogger().level))

    # Create an object to hold all cromwell configurations
    cromshell_config.obj = cromshellconfig
    update_submission_db_format(
        submission_file_path=cromshellconfig.submission_file_path
    )
    cromshellconfig.resolve_cromwell_config_server_address(server_user=cromwell_url)
    cromshellconfig.override_requests_cert_parameters(skip_certs=requests_skip_certs)
    cromshellconfig.resolve_requests_connect_timeout(timeout_cli=requests_timeout)
    cromshellconfig.resolve_gcloud_token_email(email=gcloud_token_email)
    cromshellconfig.resolve_referer_header_url(url=referer_header_url)
    cromshellconfig.resolve_color_output(
        machine_readable=machine_processable, colorful_output=colorful_output
    )


@main_entry.command()
def version():
    """Command to print the version of cromshell"""
    LOGGER.info("cromshell %s", __version__)
    print_version()


def print_version():
    """Print the version of cromshell"""
    print(f"cromshell {__version__}")


# Update with new sub-commands here. Keep in alphabetical order:
main_entry.add_command(abort.main)
main_entry.add_command(alias.main)
main_entry.add_command(cost.main)
main_entry.add_command(counts.main)
main_entry.add_command(list.main)
main_entry.add_command(list_outputs.main)
main_entry.add_command(logs.main)
main_entry.add_command(metadata.main)
main_entry.add_command(slim_metadata.main)
main_entry.add_command(status.main)
main_entry.add_command(submit.main)
main_entry.add_command(timing.main)
main_entry.add_command(update_server.main)
main_entry.add_command(validate.main)


if __name__ == "__main__":
    main_entry()  # pylint: disable=E1120
