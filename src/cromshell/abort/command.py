import logging

import click
import requests

from cromshell.utilities import http_utils, io_utils

LOGGER = logging.getLogger(__name__)


@click.command(name="abort")
@click.argument("workflow_id", required=True, nargs=-1)
@click.pass_obj
def main(config, workflow_id):
    """Abort a running workflow.

    WORKFLOW_ID can be one or more workflow ids belonging to a running workflow
    separated by a space (e.g. abort [workflow_id1] [[workflow_id2]...] )
    """

    LOGGER.info("abort")

    http_utils.assert_can_communicate_with_server(config)

    for wdl_id in workflow_id:

        requests_out = requests.post(
            f"http://34.73.109.5:8000/api/workflows/v1/{wdl_id}/abort"
        )

        http_utils.check_http_request_status_code(
            short_error_message="Failed to abort workflow.", response=requests_out
        )
        # Todo: Replace input with requests_out.json() once rebased with submit PR
        io_utils.pretty_print_json(requests_out.text)

    return 0
