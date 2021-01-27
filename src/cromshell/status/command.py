import fileinput
import json
import logging

import click
import requests
import csv

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
    config.cromwell_api_workflow_id = (
        f"{config.cromwell_server}{config.api_string}{workflow_id}"
    )

    # Set cromwell server using submission file. Running the function below with
    # passing only the workflow id overrides the default cromwell url set in the
    # cromshell config file, command line argument, and environment. This takes
    # place only if the workflow id is found in the submission file.
    cromshellconfig.resolve_cromwell_config_server_address(workflow_id=workflow_id)

    # Check if Cromwell Server Backend works
    http_utils.assert_can_communicate_with_server(config)

    # Request workflow status
    request_out = requests.get(f"{config.cromwell_api_workflow_id}/status")

    requested_status_json = request_out.content.decode("utf-8")
    workflow_status_description = json.loads(request_out.content)

    # Hold our status string here
    workflow_status = workflow_status_description["status"]

    # Set return value based on workflow status
    if workflow_status in ("Failed", "Aborted", "fail"):
        ret_val = 1
        log.display_logo(io_utils.dead_turtle)
    elif workflow_status == "Running":
        # Status claims this workflow is running fine, but we need to check to see
        # if there are any failed sub-processes.
        # To do this, we use the `execution-status-count` logic with some filtering:
        # TODO : Use this as a template for the Metadata subcommand
        # Get execution status count and filter the metadata down:
        request_meta_out = requests.get(
            f"{config.cromwell_api_workflow_id}/metadata?{config.slim_metadata_parameters}"
        )

        # metadata holds the workflow metadata as a dictionary
        metadata = json.loads(request_meta_out.content.decode("utf-8"))

        # Check for failures:
        workflow_failed = check_for_failure(metadata)
        if not workflow_failed:
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
            requested_status_json = (
                f'{{"status":"{workflow_status}","id":"{workflow_id}"}}\n{message} '
            )

    else:
        log.display_logo(io_utils.turtle)

    # Display status to user:
    line_string = requested_status_json
    print(line_string.replace(",", ",\n"))

    # Update config.submission_file:
    with fileinput.FileInput(
        config.submission_file, inplace=True, backup=".bak"
    ) as csv_file:
        reader = csv.DictReader(csv_file, delimiter="\t")
        print("\t".join(reader.fieldnames))
        for row in reader:
            if (
                row["CROMWELL_SERVER"] == config.cromwell_server
                and row["RUN_ID"] == workflow_id
            ):
                row["STATUS"] = workflow_status
                print("\t".join(x for x in row.values() if x))
            else:
                print("\t".join(x for x in row.values() if x))

    return ret_val


def check_for_failure(metadata: dict):
    """Checks a workflow metadata dictionary for failing statuses
    Returns True to indicate workflow or some task(s) has failed"""

    # If the given dictionary contains a 'status' key and has value of "Failed"
    # then exit the function returning "True" to indicate workflow has failed
    if metadata.get("status") == "Failed":
        return True

    # If the dictionary does not contain a failed value for its status key or
    # if status key does does not exist then we'll iterate through the dictionary
    # value in search of a nested dictionary (indicating subworkflows)
    # or a list which holds the task statuses.
    for value in metadata.values():

        # If a dictionary value is encountered then Depth First Search recursion
        # is used to traverse the dictionary by iterating through the given dictionary
        # and reporting whether it found a failure. The reason for this is due to the
        # tree structure of the metadata dictionary which holds the task statuses
        # in a nested dictionary key called "calls".
        if isinstance(value, dict):
            if check_for_failure(value):
                return True

        # If a list value is encountered then the dictionary being traversed through is
        # a key and value pair where the key is the task name and the value is the
        # number of times the task was executed (shard), which is normally 1 unless the
        # task was scattered. Hence the value for the key is a list to account
        # for all the shards for a task. Each item(shard) within this list is a
        # dictionary holding status for the shard.
        # We'll want to check each shard to determine whether it's status has "Failed".
        if isinstance(value, list):
            for shard in value:

                # If a key in the shared labeled "subWorkflowMetadata" then this
                # will another dictionary layer of subworkflow tasks that needs
                # to be traversed.
                if "subWorkflowMetadata" in shard.keys():
                    if check_for_failure(shard["subWorkflowMetadata"]):
                        return True
                else:
                    if shard["executionStatus"] == "Failed":
                        return True
    return False


if __name__ == "__main__":
    main()
