import json
import logging

import click
import requests

from cromshell import log
from cromshell.metadata import command as metadata_command
from cromshell.utilities import cromshellconfig, http_utils, io_utils

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
    cromshellconfig.resolve_cromwell_config_server_address(workflow_id=workflow_id)

    config.cromwell_api_workflow_id = f"{config.get_cromwell_api()}/{workflow_id}"

    # Check if Cromwell Server Backend works
    http_utils.assert_can_communicate_with_server(config)

    requested_status_json, workflow_status, updated_ret_val = query_status(
        config, workflow_id
    )
    ret_val = updated_ret_val

    # Display status to user:
    line_string = requested_status_json
    print(line_string.replace(",", ",\n"))

    # Update config.submission_file:
    io_utils.update_all_workflow_database_tsv(
        workflow_database_path=config.submission_file_path,
        workflow_id=workflow_id,
        column_to_update="STATUS",
        update_value=workflow_status,
    )

    return ret_val


def query_status(
    config, workflow_id: str, log_to_screen: bool = True
) -> (str, str, int):
    """

    :param config: object holding configurations
    :param workflow_id: ID for workflow whose status is being requested
    :param log_to_screen: whether to log to screen the status
    :return: (json string of the status, status of the workflow, return value of the main command)
    """

    ret_val = 0

    # Request workflow status
    request_out = requests.get(
        f"{config.cromwell_api_workflow_id}/status",
        timeout=config.requests_connect_timeout,
        verify=config.requests_verify_certs,
    )
    requested_status_json = request_out.content.decode("utf-8")
    workflow_status_description = json.loads(request_out.content)
    # Hold our status string here
    workflow_status = workflow_status_description["status"]
    # Set return value based on workflow status
    if (
        workflow_status
        in cromshellconfig.WorkflowStatuses.Failed.value
        + cromshellconfig.WorkflowStatuses.Aborted.value
    ):
        ret_val = 1
        if log_to_screen:
            log.display_logo(io_utils.dead_turtle)
    elif workflow_status == "Running":
        # Status claims this workflow is running fine, but we need to check to see
        # if there are any failed sub-processes.
        # To do this, we get the workflow metadata and search for any failures
        formatted_metadata_parameter = metadata_command.format_metadata_params(
            list_of_keys=config.SLIM_METADATA_DEFAULT_KEYS,
            exclude_keys=False,
            expand_subworkflows=True,
        )

        request_meta_out = requests.get(
            f"{config.cromwell_api_workflow_id}/metadata",
            params=formatted_metadata_parameter,
            timeout=config.requests_connect_timeout,
            verify=config.requests_verify_certs,
        )

        # metadata holds the workflow metadata as a dictionary
        metadata = json.loads(request_meta_out.content.decode("utf-8"))

        # Check for failures:
        if not workflow_failed(metadata):
            # We could not find 'Fail' in our metadata, so our
            # original Running status is correct.
            if log_to_screen:
                log.display_logo(io_utils.turtle)
        else:
            if log_to_screen:
                log.display_logo(io_utils.doomed_logo)
            workflow_status = cromshellconfig.WorkflowStatuses.DOOMED.value[0]
            message = (
                "The workflow is Running but one of the instances "
                "has failed which will lead to failure."
            )
            requested_status_json = (
                f'{{"status":"{workflow_status}","id":"{workflow_id}"}}\n{message} '
            )

    else:
        if log_to_screen:
            log.display_logo(io_utils.turtle)
    return requested_status_json, workflow_status, ret_val


def workflow_failed(metadata: dict):
    """Checks a workflow metadata dictionary for failing statuses
    Returns True to indicate workflow or some task(s) has failed"""

    # If the given dictionary contains a 'status' key and has value of "Failed"
    # then exit the function returning "True" to indicate workflow has failed
    if metadata.get("status") == cromshellconfig.WorkflowStatuses.Failed.value[0]:
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
            if workflow_failed(value):
                return True

        # If a list value is encountered then the dictionary being traversed through is
        # a key and value pair where the key is the task name and the value is the
        # number of times the task was executed (shard), which is normally 1 unless the
        # task was scattered. Hence the value for the key is a list to account
        # for all the shards for a task. Each item(shard) within this list is a
        # dictionary holding status for the shard.
        # We'll want to check each shard to determine whether it's status has "Failed".
        elif isinstance(value, list):
            for shard in value:

                # If a key in the shard is labeled "subWorkflowMetadata", then this
                # will contain another dictionary layer of subworkflow tasks that will
                # require traversal.
                if "subWorkflowMetadata" in shard.keys():
                    if workflow_failed(shard["subWorkflowMetadata"]):
                        return True
                else:
                    if (
                        shard["executionStatus"]
                        == cromshellconfig.WorkflowStatuses.Failed.value[0]
                    ):
                        return True
    return False


if __name__ == "__main__":
    main()
