import logging

import click
import requests

import cromshell.utilities.http_utils as http_utils
import cromshell.utilities.io_utils as io_utils
from cromshell.utilities import command_setup_utils

LOGGER = logging.getLogger(__name__)


@click.command(name="list-outputs")
@click.argument("workflow_ids", required=True, nargs=-1)
@click.pass_obj
def main(config, workflow_ids):
    """List workflow outputs."""

    LOGGER.info("list-outputs")

    return_code = 0

    for workflow_id in workflow_ids:
        command_setup_utils.resolve_workflow_id_and_server(
            workflow_id=workflow_id, cromshell_config=config
        )

        requests_out = requests.get(
            f"{config.cromwell_api_workflow_id}/outputs",
            timeout=config.requests_connect_timeout,
            verify=config.requests_verify_certs,
            headers=http_utils.generate_headers(config),
        )

        if requests_out.ok:
            io_utils.pretty_print_json(format_json=requests_out.json())
        else:
            return_code = 1

            http_utils.check_http_request_status_code(
                short_error_message="Failed to retrieve workflow outputs.",
                response=requests_out,
                # Raising exception is set false to allow
                # command to retrieve outputs of remaining workflows.
                raise_exception=False,
            )

    return return_code



