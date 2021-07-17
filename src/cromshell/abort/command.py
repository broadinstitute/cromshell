import logging

import click
import requests

from cromshell.utilities import cromshellconfig, http_utils, io_utils

LOGGER = logging.getLogger(__name__)


@click.command(name="abort")
@click.argument("workflow_ids", required=True, nargs=-1)
@click.pass_obj
def main(config, workflow_ids):
    """Abort a running workflow.

    WORKFLOW_ID can be one or more workflow ids belonging to a running workflow
    separated by a space (e.g. abort [workflow_id1] [[workflow_id2]...]).

    """

    LOGGER.info("abort")

    return_code = 0

    for wdl_id in workflow_ids:

        cromshellconfig.resolve_cromwell_config_server_address(workflow_id=wdl_id)

        http_utils.assert_can_communicate_with_server(config)

        requests_out = requests.post(
            f"{config.cromwell_server}{config.API_STRING}/{wdl_id}/abort"
        )

        if requests_out.ok:
            # Todo: Replace input with requests_out.json() once rebased with submit PR
            io_utils.pretty_print_json(requests_out.text)
        else:
            return_code = 1

            http_utils.check_http_request_status_code(
                short_error_message="Failed to abort workflow.",
                response=requests_out,
                # Raising exception is set to false to allow
                # command to abort remaining workflows.
                raise_exception=False,
            )

    return return_code
