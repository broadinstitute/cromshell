import fileinput
import json
import logging
import re

import click
import requests
from typing_extensions import Counter

from cromshell.utilities import cromshellconfig
from cromshell.utilities import http_utils
from cromshell.utilities import io_utils
from cromshell import log

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

    requested_status_json = request_out.content.decode("utf-8")
    workflow_status_description = json.loads(request_out.content)

    # Hold our status string here
    workflow_status = workflow_status_description["status"]

    # Set return value based on workflow status
    if workflow_status in ("Failed", "Aborted", "fail"):
        ret_val = 1
        log.display_logo(io_utils.dead_turtle)
    elif workflow_status == "Succeeded":  # change to Running for the final version.
        # Status claims this workflow is running fine, but we need to check to see
        # if there are any failed sub-processes.
        # To do this, we use the `execution-status-count` logic with some filtering:
        # TODO : Use this as a template for the Metadata subcommand
        # Get execution status count and filter the metadata down:
        request_meta_out = requests.get(
            f"{config.cromwell_server}{config.api_string}{workflow_id}/metadata?{config.slim_metadata_parameters}"
        )

        # tmp_metadata holds the workflow metadata as a dictionary
        tmp_metadata = json.loads(request_meta_out.content.decode("utf-8"))
        execution_status_count = get_metadata_status_summary(tmp_metadata)

        # Check for failure states:
        failed = False
        for task_status in execution_status_count:
            for key in task_status:
                if "Failed" in str(task_status[key]):
                    failed = True
                    break

        # Check for failures:
        if not failed:
            # We could not find 'Fail' in our metadata, so our
            # original Running status is correct.
            log.display_logo(io_utils.turtle)
        else:
            log.display_logo(io_utils.doomed_logo)
            workflow_status = "DOOMED"
            message = (
                "The workflow is Running but one of the instances "
                "has failed which will lead to failure."
            )
            requested_status_json = f'{{"status":"{workflow_status}","id":"{workflow_id}"}}\n{message}'

    else:
        log.display_logo(io_utils.turtle)

    # Display status to user:
    line_string = requested_status_json
    print(line_string.replace(",", ",\n"))

    # Update ${CROMWELL_SUBMISSIONS_FILE}:
    with fileinput.FileInput(
            config.submission_file, inplace=True, backup=".bak"
    ) as f:
        for line in f:
            if config.cromwell_server and workflow_id in line:
                pattern = "\t[^\t]+$"
                replace = "\t" + workflow_status  ##split by tab and replace the 5th element
                updated_line = re.sub(pattern, replace, line)
                print(updated_line, end="\n")
            else:
                print(line, end="")

    return ret_val


def get_metadata_status_summary(workflow_metadata):
    """Get the status for each call in a workflow and the frequency of those statuses"""
    # workflow_metadata holds the workflow metadata as a dictionary
    workflow_status_count = []
    tmp_execution_status = []

    # For each call in the metadata dictionary create a shortened summary containing the call name and status
    for call in workflow_metadata['calls']:
        call_element = f'"{call}": '
        execution_statuses = []

        # For each call name add the number of executionstatus to a list
        for instanceDic in workflow_metadata['calls'][call]:
            execution_statuses.append(instanceDic['executionStatus'])

        # Create a key and value pair for the execution status and number of times it is seen
        status_count = Counter(execution_statuses)
        # For each status for the call add the call name and status name and count to list
        for status in set(execution_statuses):
            status_element = f'{{"{status}": {status_count[status]}}}'
            tmp_execution_status.append(f"{call_element}{status_element}")

    #
    tmp_execution_status_json = ", ".join(tmp_execution_status)
    tmp_execution_status_json = "{" + tmp_execution_status_json + "}"
    workflow_status_count.append(json.loads(tmp_execution_status_json))

    return workflow_status_count


if __name__ == '__main__':
    main()
