import fileinput
import json
import logging
import re

import click
import jq
import requests

from cromshell.utilities import cromshellconfig
from cromshell.utilities import http_utils
from cromshell.utilities import io_utils

LOGGER = logging.getLogger(__name__)


@click.command(name="status")
@click.argument("workflow_id")
@click.pass_obj
def main(config, workflow_id):
    """Check the status of a Cromwell job UUID"""

    LOGGER.info("status")

    ret_val = 0

    # Set cromwell server using submission file. Running the function below with
    # passing only the workflow id overrides the default cromwell url set in the
    # cromshell config file, command line argument, and environment. This takes
    # place only if the workflow id is found in the submission file.
    cromshellconfig.resolve_cromwell_config_server_address(
        workflow_id=workflow_id
    )

    # Check if Cromwell Server Backend works
    http_utils.assert_can_communicate_with_server(config)

    # Request workflow status
    request_out = requests.get(
        f"{config.cromwell_server}{config.api_string}{workflow_id}/status"
    )

    requested_status_json = request_out.content
    workflow_status_description = json.loads(request_out.content)

    # Hold our status string here
    workflow_status = workflow_status_description["status"]

    # Set return value based on workflow status
    if workflow_status in ("Failed", "Aborted", "fail"):
        ret_val = 1
        io_utils.turtle_dead(config.show_logo)
    elif workflow_status == "Succeeded":  # change to Running for the final version.
        # Status claims this workflow is running fine, but we need to check to see
        # if there are any failed sub-processes.
        # To do this, we use the `execution-status-count` logic with some filtering:

        # Get execution status count and filter the metadata down:
        request_meta_out = requests.get(
            f"{config.cromwell_server}{config.api_string}{workflow_id}/metadata?{config.slim_metadata_parameters}"
        )

        execution_status_count = (
            jq.compile(
                ".. | .calls? | values | map_values(group_by(.executionStatus) | "
                "map({(.[0].executionStatus): . | length}) | add)"
            )
            .input(json.loads(request_meta_out.content))
            .all()
        )

        # Check for failure states:
        failed = False
        for task_status in execution_status_count:
            for key in task_status:
                if re.search("Failed", str(task_status[key]), re.I):
                    failed = True
                    break

        # Check for failures:
        if failed:
            # We could not find 'Fail' in our metadata, so our
            # original Running status is correct.
            io_utils.turtle(config.show_logo)
        else:
            io_utils.doomed_logo(config.show_logo)
            workflow_status = "DOOMED"
            message = (
                "The workflow is Running but one of the instances "
                "has failed which will lead to failure."
            )
            requested_status_json = f'{{"status":"{workflow_status}","id":"{workflow_id}"}}\n{message}'

    else:
        io_utils.turtle(config.show_logo)

    # Display status to user:
    line_string = requested_status_json
    print(line_string.replace(",", ",\n"))

    # Update ${CROMWELL_SUBMISSIONS_FILE}:
    with open(config.submission_file) as file:
        # Check if workflow Id is submission file, if so update file.
        if workflow_id in file.read():
            # Open file for writing and make backup of file
            with fileinput.FileInput(
                config.submission_file, inplace=True, backup=".bak"
            ) as f:
                pattern = "\t[^\t]+$"
                replace = "\t" + workflow_status
                for line in f:
                    if config.cromwell_server and workflow_id in line:
                        updated_line = re.sub(pattern, replace, line)
                        print(updated_line, end="\n")
                    else:
                        print(line, end="")

    return ret_val
