import logging
import webbrowser

import click

from cromshell import log
from cromshell.utilities import cromshellconfig, http_utils, io_utils

LOGGER = logging.getLogger(__name__)


@click.command(name="timing")
@click.argument("workflow_id")
@click.pass_obj
def main(config, workflow_id):
    """Open the timing diagram in a browser"""

    LOGGER.info("timing")

    ret_val = 0

    # Set cromwell server using submission file. Running the function below with
    # passing only the workflow id overrides the default cromwell url set in the
    # cromshell config file, command line argument, and environment. This takes
    # place only if the workflow id is found in the submission file.
    cromshellconfig.resolve_cromwell_config_server_address(workflow_id=workflow_id)

    # Check if Cromwell Server Backend works
    http_utils.assert_can_communicate_with_server(config)

    # Print some status info.
    log.display_logo(io_utils.turtle)
    LOGGER.info(
        "Opening timing information in your default web browser for job ID: %s",
        workflow_id,
    )

    # Open the system's default web browser and navigate to the timing diagram page.
    server_url_for_browser = (
        f"{cromshellconfig.cromwell_server}/api/workflows/v1/{workflow_id}/timing"
    )
    webbrowser.open_new_tab(server_url_for_browser)

    return ret_val


if __name__ == "__main__":
    main()
