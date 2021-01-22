import fileinput
import json
import logging

import click
import requests
import csv
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

        # tmp_metadata holds the workflow metadata as a dictionary
        tmp_metadata = json.loads(request_meta_out.content.decode("utf-8"))
        summarized_tmp_metadata = get_tasks_status(tmp_metadata)
        execution_status_count = get_metadata_status_summary(summarized_tmp_metadata)

        # Check for failure states:
        failed = False
        for call in execution_status_count:
            if "Failed" in str(execution_status_count[call]):
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


def get_tasks_status(metadata_json: dict):
    """Summarizes a given workflow metadata dictionary into a
    new dictionary with only task name and status"""
    current_task_status = {}
    subworkflow_task_status = {}
    task_status = {}
    for key, value in metadata_json.items():
        # Skip any keys that have values that are strings, because we are not
        # interested in them
        if isinstance(value, str):
            continue

        # If a dictionary value is encountered then recursion is used iterate through
        # the dictionary to find call statuses. The reason for this is due to the tree
        # structure of the metadata dictionary which holds the calls, subworkflow calls,
        # and their status within layers of the dictionary. Depth First Search recursion
        # is used to traverse the dictionary by iterating through any dictionary this
        # this functions comes across first and obtaining their call and status.
        if isinstance(value, dict):
            current_task_status = get_tasks_status(value)

        # If a list value is encountered then the dictionary being traversed through is
        # a key and value pair where the key is the task name and the value is the
        # number of times the task was executed (shard), which is normally 1 unless the
        # task was scattered. Hence the value for the key is a list to account
        # for all the shards for a task. Each item(shard) within this list is a
        # dictionary holding status for the shard.
        # We'll want to add this key and list value holding all its shard(s)
        # to the temp dictionary.
        if isinstance(value, list):
            # Since each item in the list is a shard of a task we'll iterate through
            # the list and collect info on all shards
            task_status[key] = list()
            for i, shard in enumerate(value):
                # If a key in the shard dictionary has the term "subWorkflowMetadata"
                # then this is a subworkflow containing another layer of tasks
                # so we iterate through the dictionary to obtain its task statuses
                if "subWorkflowMetadata" in shard.keys():
                    subworkflow_task_status = get_tasks_status(shard["subWorkflowMetadata"])
                    # Remove "Scatter" key from dict
                    if key in task_status.keys():
                        task_status.pop(key)
                # If there isn't a sub workflow then we add the task name combined
                # with the shard index as a key and its metadata dictionary as its
                # value
                else:
                    task_status[key].append(shard)

    # Merge all the dictionaries together from all the different if statments
    merged_dic = {**current_task_status, **subworkflow_task_status, **task_status}
    return merged_dic


def get_metadata_status_summary(workflow_call_metadata):
    """Get the status for each call in a workflow
    and the frequency of those statuses"""

    tmp_execution_status = {}

    # For each call in the given metadata dictionary create a shortened dictionary
    # containing the call name and status
    for call in workflow_call_metadata:
        execution_statuses = []  # List to hold the different status per call
        tmp_execution_status[call] = {}

        # For each call name add the number of execution_status to a list
        for shard in workflow_call_metadata[call]:
            execution_statuses.append(shard["executionStatus"])

        # Create a key and value pair for the execution status and number of times
        # it is seen for this call
        status_count = Counter(execution_statuses)

        # For each status for the call add the call name and status name and count
        # to list
        for status in set(execution_statuses):
            tmp_execution_status[call][status] = status_count[status]

    return tmp_execution_status


if __name__ == "__main__":
    main()
