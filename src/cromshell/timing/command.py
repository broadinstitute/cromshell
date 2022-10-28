import logging
import webbrowser

import click

from cromshell import log
from cromshell.utilities import command_setup_utils, io_utils

LOGGER = logging.getLogger(__name__)


@click.command(name="timing")
@click.argument("workflow_id")
@click.pass_obj
def main(config, workflow_id):
    """Open the timing diagram in a browser"""

    LOGGER.info("timing")

    ret_val = 0

    command_setup_utils.resolve_workflow_id_and_server(
        workflow_id=workflow_id, cromshell_config=config
    )

    # Print some status info.
    log.display_logo(io_utils.turtle)
    LOGGER.info(
        "Opening timing information in your default web browser for job ID: %s",
        workflow_id,
    )

    # Open the system's default web browser and navigate to the timing diagram page.
    server_url_for_browser = f"{config.cromwell_api_workflow_id}/timing"
    webbrowser.open_new_tab(server_url_for_browser)

    return ret_val


if __name__ == "__main__":
    main()
