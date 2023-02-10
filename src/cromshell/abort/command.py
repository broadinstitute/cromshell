import logging

import click
import requests

from cromshell.utilities import command_setup_utils, http_utils, io_utils

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
        command_setup_utils.resolve_workflow_id_and_server(
            workflow_id=wdl_id, cromshell_config=config
        )

        requests_out = requests.post(
            f"{config.cromwell_api_workflow_id}/abort",
            headers=http_utils.generate_headers(config),
        )

        if requests_out.ok:
            io_utils.pretty_print_json(format_json=requests_out.json())
        else:
            return_code = 1

            http_utils.check_http_request_status_code(
                short_error_message="Failed to abort workflow.",
                response=requests_out,
                # Raising exception is set false to allow
                # command to abort remaining workflows.
                raise_exception=False,
            )

    return return_code
