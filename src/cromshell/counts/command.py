import logging
from itertools import groupby
from typing import Dict

import click
from termcolor import colored

from cromshell.log import DelayedLogMessage
from cromshell.metadata import command as metadata_command
from cromshell.utilities import http_utils, io_utils, workflow_id_utils
from cromshell.utilities.cromshellconfig import TaskStatus

LOGGER = logging.getLogger(__name__)


@click.command(name="counts")
@click.argument("workflow_ids", required=True, nargs=-1)
@click.option(
    "-j",
    "--json-summary",
    is_flag=True,
    default=False,
    help="Print a json summary of the task status counts",
)
@click.option(
    "-x",
    "--compress-subworkflows",
    is_flag=True,
    default=False,
    help="Compress sub-workflow metadata information",
)
@click.pass_obj
def main(config, workflow_ids, json_summary, compress_subworkflows):
    """
    Get the summarized statuses of all tasks in the workflow.

    WORKFLOW_ID can be one or more workflow ids belonging to a
    running workflow separated by a space.
    (e.g. counts [workflow_id1] [[workflow_id2]...])

    """

    LOGGER.info("counts")

    for workflow_id in workflow_ids:
        resolved_workflow_id = workflow_id_utils.resolve_workflow_id(
            cromshell_input=workflow_id,
            submission_file_path=config.submission_file_path,
        )

        http_utils.set_and_check_cromwell_server(
            config=config, workflow_id=resolved_workflow_id
        )

        # Get metadata
        formatted_metadata_parameter = metadata_command.format_metadata_params(
            list_of_keys=config.METADATA_KEYS_TO_OMIT,
            exclude_keys=True,
            expand_subworkflows=not compress_subworkflows,
        )

        workflow_metadata = metadata_command.get_workflow_metadata(
            meta_params=formatted_metadata_parameter,
            api_workflow_id=config.cromwell_api_workflow_id,
            timeout=config.requests_connect_timeout,
            verify_certs=config.requests_verify_certs,
            headers=http_utils.generate_headers(config),
        )

        if json_summary:
            print_task_status_summary(workflow_metadata=workflow_metadata)
        else:
            pretty_status_counts(
                workflow_id=resolved_workflow_id,
                workflow_metadata=workflow_metadata,
            )

        DelayedLogMessage.display_log_messages()
    return 0


def pretty_status_counts(workflow_id: str, workflow_metadata: dict) -> None:
    """
    Prints the workflow status and runs the function to print
    the workflow status summary.

    :param workflow_id: Hexadecimal identifier of workflow submission
    :param workflow_metadata: Metadata of the workflow to process
    :return:
    """
    workflow_status = workflow_metadata.get("status")
    print(
        colored(
            workflow_id + "\t" + workflow_status,
            color=io_utils.TextStatusesColor.COLOR_UNDERLINED["color"],
            attrs=io_utils.TextStatusesColor.COLOR_UNDERLINED["attrs"],
        )
    )
    print_workflow_status(
        workflow_metadata=workflow_metadata,
        indent="\t",
    )


def print_workflow_status(workflow_metadata: dict, indent: str) -> None:
    """
    Recursively parses a (sub-)workflow's metadata and prints out
    the summary on its tasks statuses.
    :param workflow_metadata: Metadata of the workflow to process
    :param indent: Indent string given as "\t", used to indent print out
    :return:
    """
    calls_metadata = workflow_metadata["calls"]
    calls = list(calls_metadata.keys())

    for call in calls:
        # If task has a key called 'subworkflowMetadata' in its
        # first (zero) element (shard) then perform recursion.
        if "subWorkflowMetadata" in calls_metadata[call][0]:
            sub_workflow_name = call
            sub_calls = calls_metadata[sub_workflow_name]
            print(f"{indent}SubWorkflow {sub_workflow_name}")

            # For each call in subworkflow calls get the subworkflow metadata.
            # This loop will go through each shard if task is scattered
            for sub_call in sub_calls:
                print_workflow_status(
                    workflow_metadata=sub_call["subWorkflowMetadata"],
                    indent=indent + "\t",
                )

        # If no subworkflow is found then print status summary for task
        else:
            print_call_status(
                call=call, indent=indent, workflow_calls_metadata=calls_metadata
            )


def print_call_status(call: str, indent: str, workflow_calls_metadata: dict) -> None:
    """
    Prints the task name and status count

    :param call: Name of the call to print
    :param indent: Indent string given as "\t", used to indent print out
    :param workflow_calls_metadata: The 'calls' of the workflow to process
    :return:
    """

    # Scattered task calls and unscattered calls are treated similarly.
    # Thus, `shards` list can either have one item (-1) representing an unscattered
    # task call, or multiple items (0,1,...N) representing scattered task
    shards: list = workflow_calls_metadata[call]

    shard_status_count: dict = get_shard_status_count(shards)

    shards_done = shard_status_count.get(TaskStatus.DONE.value, 0)
    shards_running = shard_status_count.get(TaskStatus.RUNNING.value, 0)
    shards_failed = shard_status_count.get(TaskStatus.FAILED.value, 0)
    shards_retried = shard_status_count.get(TaskStatus.RETRYABLEFAILURE.value, 0)
    shards_unknown, unknown_shard_status = get_unknown_status(
        shard_status_count=shard_status_count, known_statuses=TaskStatus.list()
    )

    # Determine what color to print task summary
    if shards_failed == 0 and shards_running == 0:
        task_status_font = io_utils.TextStatusesColor.TASK_COLOR_SUCCEEDED
    elif shards_failed > 0 and shards_running > 0:  # Running but will fail
        task_status_font = io_utils.TextStatusesColor.TASK_COLOR_FAILING
    elif shards_running > 0:
        task_status_font = io_utils.TextStatusesColor.TASK_COLOR_RUNNING
    elif shards_failed > 0:
        task_status_font = io_utils.TextStatusesColor.TASK_COLOR_FAILED
    else:  # catch all
        task_status_font = "yellow"

    # Format and print task summary
    formatted_task_summary = (
        f"{indent}{call}\t{shards_running} Running, "
        f"{shards_done} Done, {shards_retried} Preempted, {shards_failed} Failed"
    )

    print(colored(formatted_task_summary, color=task_status_font))

    # If the task has shards that failed list them
    if shards_failed:
        failed_shards_index = get_list_of_failed_shards(shards=shards)
        if failed_shards_index != [-1]:  # Prints only if task was scattered
            # Format and print task failed shards
            failed_shards_summary = f"{indent}Failed shards: {failed_shards_index}"
            print(colored(failed_shards_summary, color=task_status_font))

    # If unknown status present append its count to print out.
    if shards_unknown > 0:
        formatted_task_summary += f", {shards_unknown} Unknown"
        DelayedLogMessage.save_log_message(
            log_level=logging.WARNING,
            log_message="Cromshell found the following unknown task status(es) "
            f"{unknown_shard_status}, an unknown task status is a status that does "
            f"not match the following known task statuses:  {TaskStatus.list()} . "
            "Please report all relevant info to Cromshell git repository so we can "
            "improve our code. Thank You.",
        )


def print_task_status_summary(workflow_metadata: dict) -> None:
    """
    Prints the status count for each task in a workflow.
    Does NOT run expose subworkflows

    :param workflow_metadata: Metadata of the workflow to process
    :return:
    """

    workflow_status_summary = {}
    for task in workflow_metadata["calls"]:
        shards = workflow_metadata["calls"][task]

        # Add the status counts for this task to dictionary holding other
        # task status counts
        workflow_status_summary[task] = get_shard_status_count(shards)

    io_utils.pretty_print_json(format_json=workflow_status_summary)


def get_shard_status_count(shards: list) -> Dict[str, int]:
    """
    Count the number of shards for each status type and return as dictionary.
    :param shards: The metadata for all shards in a scatter or shard of a single task
    :return:
    """

    statuses_counts = {}
    grouped_shards = group_shards_by_status(shards=shards)

    for status in grouped_shards:
        statuses_counts[status] = len(grouped_shards[status])

    return statuses_counts


def get_list_of_failed_shards(shards: list) -> list:
    """
    Get a list of the failed shards' indexes
    :param shards: The metadata for all shards in a scatter or shard of a single task
    :return:
    """

    return [
        shard["shardIndex"]
        for shard in group_shards_by_status(shards=shards).get("Failed", list())
    ]


def group_shards_by_status(shards: list) -> Dict[str, list]:
    """
    Groups shards by their status
    :param shards: The metadata for all shards in a scatter or shard of a single task
    :return:
    """
    grouped_shards = {}
    sorted_shards = sorted(shards, key=lambda y: y["executionStatus"])
    for status, group in groupby(sorted_shards, lambda x: x["executionStatus"]):
        grouped_shards[status] = list(group)
    return grouped_shards


def get_unknown_status(
    shard_status_count: Dict[str, int], known_statuses: list
) -> (int, str):
    """
    Returns the name and the total shard count for statuses that do not match the normal
    known statuses (Done, Failed, Running, etc.)
    :param shard_status_count: Dictionary having key=status and value=status_count
    :param known_statuses: List of statuses
    :return: Total number of unknown shard counts and list of unknown status names
    """
    shards_unknown = 0
    unknown_shard_status = []
    for status in shard_status_count.keys():
        if status not in known_statuses:
            shards_unknown += shard_status_count[status]
            unknown_shard_status.append(status)

    return shards_unknown, unknown_shard_status
