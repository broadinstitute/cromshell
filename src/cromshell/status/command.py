import fileinput
import json
import logging
import re
import sys

import click
import jq
import requests

from cromshell.utilities import CromshellConfig, HTTPUtils, IOUtils

LOGGER = logging.getLogger(__name__)


@click.command(name="status")
@click.argument("workflow_id")
@click.pass_obj
def main(cromshell_config, workflow_id):
    """Check the status of a Cromwell job UUID"""
    if cromshell_config.is_verbose:
        LOGGER.info("status")
    else:
        click.echo("status")

    ret_val = 0

    # Set cromwell server using submission file. Running the function below with passing only the workflow id
    # overrides the default cromwell url set in the cromshell config file, command line argument, and
    # environment. This takes place only if the workflow id is found in the submission file.
    CromshellConfig.CromshellConfig.override_cromwell_config_server(
        workflow_id=workflow_id
    )

    # Check if Cromwell Server Backend works
    HTTPUtils.assert_can_communicate_with_server(cromshell_config.cromwell_server)

    # Request workflow status
    request_out = requests.get(
        "{}/api/workflows/v1/{}/status".format(
            cromshell_config.cromwell_server, workflow_id
        )
    )

    requested_status_json = request_out.content
    workflow_status_description = json.loads(request_out.content)

    # Hold our status string here
    workflow_status = workflow_status_description["status"]

    # Set return value based on workflow status
    if workflow_status in ("Failed", "Aborted", "fail"):
        ret_val = 1
        IOUtils.turtle_dead(cromshell_config.is_verbose)
    elif workflow_status == "Succeeded":  # change to Running for the final version.
        # Status claims this workflow is running fine, but we need to check to see
        # if there are any failed sub-processes.
        # To do this, we use the `execution-status-count` logic with some filtering:

        # Get execution status count and filter the metadata down:
        request_meta_out = requests.get(
            "{}/api/workflows/v1/{}/metadata?{}".format(
                cromshell_config.cromwell_server,
                workflow_id,
                cromshell_config.slim_metadata_parameters,
            )
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
        if not failed:
            # We could not find 'Fail' in our metadata, so our original Running status is correct.
            IOUtils.turtle(cromshell_config.is_verbose)
        else:
            IOUtils.doomed_logo(cromshell_config.is_verbose)
            workflow_status = "DOOMED"
            message = "The workflow is Running but one of the instances has failed which will lead to failure."
            temp_line = '{{"status":"{}","id":"{}"}}{}{}'.format(
                workflow_status, workflow_id, "\n", message
            )
            new_temp_file = bytes(temp_line.encode())
            requested_status_json = new_temp_file

    else:
        IOUtils.turtle(cromshell_config.is_verbose)

    # Display status to user:
    line_string = requested_status_json.decode("utf-8")
    click.echo(line_string.replace(",", ",\n"))

    # Update ${CROMWELL_SUBMISSIONS_FILE}:
    with open(cromshell_config.submission_file) as file:
        # Check if workflow Id is submission file, if so update file.
        if workflow_id in file.read():
            # Open file for writing and make backup of file
            with fileinput.FileInput(
                cromshell_config.submission_file, inplace=True, backup=".bak"
            ) as f:
                pattern = "\t[^\t]+$"
                replace = "\t" + workflow_status
                for line in f:
                    if cromshell_config.cromwell_server and workflow_id in line:
                        updated_line = re.sub(pattern, replace, line)
                        print(updated_line, end="\n")
                    else:
                        print(line, end="")

    return ret_val
