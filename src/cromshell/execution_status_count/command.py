import json
import logging
from itertools import groupby

import click
from termcolor import colored

from cromshell.metadata import command as metadata_command
from cromshell.utilities import io_utils, workflow_id_utils

LOGGER = logging.getLogger(__name__)


@click.command(name="execution-status-count")
@click.argument("workflow_id")
@click.option(
    "-p",
    "--pretty-print",
    is_flag=True,
    default=False,
    help="Enable pretty-printing",
)
@click.option(
    "-x",
    "--expand-subworkflows",
    is_flag=True,
    default=False,
    help="Expand sub-workflow information",
)
@click.pass_obj
def main(config, workflow_id, pretty_print, expand_subworkflows):
    """
    Get the summarized status of all jobs in the workflow.
    """

    LOGGER.info("execution-status-count")

    # resolved_workflow_id = workflow_id_utils.resolve_workflow_id(
    #     cromshell_input=workflow_id,
    #     submission_file_path=config.submission_file_path,
    # )
    #
    # # Todo: the function below also sets the config.cromwell_api_workflow_id but should
    # #  probably not be in the same function or atleast rename to make it more clear
    # metadata_command.check_cromwell_server(config=config, workflow_id=resolved_workflow_id)

    # # Get metadata
    # formatted_metadata_parameter = metadata_command.format_metadata_params(
    #     list_of_keys=config.METADATA_KEYS_TO_OMIT,
    #     exclude_keys=True,
    #     expand_subworkflows=True,
    # )
    #
    # workflow_meta_data = metadata_command.get_workflow_metadata(
    #     meta_params=formatted_metadata_parameter,
    #     api_workflow_id=config.cromwell_api_workflow_id,
    #     timeout=config.requests_connect_timeout,
    #     verify_certs=config.requests_verify_certs,
    # )

    # workflow_metadata = {'workflowName': 'HelloWorld', 'workflowProcessingEvents': [{'cromwellId': 'cromid-f6be9e3', 'description': 'Finished', 'timestamp': '2022-01-07T21:44:13.768Z', 'cromwellVersion': '67-a4567f6'}, {'cromwellId': 'cromid-f6be9e3', 'description': 'PickedUp', 'timestamp': '2022-01-07T21:43:58.194Z', 'cromwellVersion': '67-a4567f6'}], 'actualWorkflowLanguageVersion': 'draft-2', 'calls': {'HelloWorld.HelloWorldTask': [{'retryableFailure': False, 'executionStatus': 'Failed', 'stdout': '/cromwell-executions/HelloWorld/c1b16617-4bd5-40b0-b899-426bbc68656b/call-HelloWorldTask/execution/stdout', 'backendStatus': 'Done', 'compressedDockerSize': 4980136, 'commandLine': "    set -e\necho 'Hello World!'", 'shardIndex': -1, 'runtimeAttributes': {'maxRetries': '0', 'continueOnReturnCode': '0', 'docker': 'frolvlad/alpine-bash', 'failOnStderr': 'false'}, 'callCaching': {'allowResultReuse': False, 'effectiveCallCachingMode': 'CallCachingOff'}, 'inputs': {'default_ram_mb': 3072, 'disk_space_gb': None, 'machine_mem': 3072, 'default_disk_space_gb': 100, 'preemptible_attempts': None, 'use_ssd': False, 'docker': 'frolvlad/alpine-bash', 'command_mem': 2048, 'boot_disk_size_gb': None, 'mem': None, 'cpu': None, 'default_boot_disk_size_gb': 15}, 'returnCode': -1, 'failures': [{'message': "Job HelloWorld.HelloWorldTask:NA:1 exited with return code -1 which has not been declared as a valid return code. See 'continueOnReturnCode' runtime attribute for more details.", 'causedBy': []}], 'jobId': '243', 'backend': 'Local', 'end': '2022-01-07T21:44:13.312Z', 'stderr': '/cromwell-executions/HelloWorld/c1b16617-4bd5-40b0-b899-426bbc68656b/call-HelloWorldTask/execution/stderr', 'callRoot': '/cromwell-executions/HelloWorld/c1b16617-4bd5-40b0-b899-426bbc68656b/call-HelloWorldTask', 'attempt': 1, 'executionEvents': [{'startTime': '2022-01-07T21:44:12.331Z', 'description': 'UpdatingJobStore', 'endTime': '2022-01-07T21:44:13.314Z'}, {'startTime': '2022-01-07T21:44:09.078Z', 'description': 'RunningJob', 'endTime': '2022-01-07T21:44:12.331Z'}, {'startTime': '2022-01-07T21:44:07.457Z', 'description': 'WaitingForValueStore', 'endTime': '2022-01-07T21:44:07.473Z'}, {'endTime': '2022-01-07T21:44:09.078Z', 'startTime': '2022-01-07T21:44:07.473Z', 'description': 'PreparingJob'}, {'startTime': '2022-01-07T21:44:01.538Z', 'description': 'Pending', 'endTime': '2022-01-07T21:44:01.554Z'}, {'startTime': '2022-01-07T21:44:01.554Z', 'description': 'RequestingExecutionToken', 'endTime': '2022-01-07T21:44:07.457Z'}], 'start': '2022-01-07T21:44:01.519Z'}]}, 'outputs': {}, 'workflowRoot': '/cromwell-executions/HelloWorld/c1b16617-4bd5-40b0-b899-426bbc68656b', 'actualWorkflowLanguage': 'WDL', 'id': 'c1b16617-4bd5-40b0-b899-426bbc68656b', 'inputs': {'HelloWorld.mem': None, 'HelloWorld.HelloWorldTask.default_disk_space_gb': 100, 'HelloWorld.disk_space_gb': None, 'HelloWorld.docker': 'frolvlad/alpine-bash', 'HelloWorld.HelloWorldTask.default_ram_mb': 3072, 'HelloWorld.cpu': None, 'HelloWorld.HelloWorldTask.default_boot_disk_size_gb': 15, 'HelloWorld.boot_disk_size_gb': None, 'HelloWorld.HelloWorldTask.use_ssd': False, 'HelloWorld.preemptible_attempts': None}, 'labels': {'cromwell-workflow-id': 'cromwell-c1b16617-4bd5-40b0-b899-426bbc68656b'}, 'submission': '2022-01-07T21:43:56.107Z', 'status': 'Failed', 'failures': [{'causedBy': [{'message': "Job HelloWorld.HelloWorldTask:NA:1 exited with return code -1 which has not been declared as a valid return code. See 'continueOnReturnCode' runtime attribute for more details.", 'causedBy': []}], 'message': 'Workflow failed'}], 'end': '2022-01-07T21:44:13.767Z', 'start': '2022-01-07T21:43:58.228Z'}
    with open("/Users/bshifaw/Downloads/metadata-big.json", "r") as ff:
        workflow_metadata = json.load(ff)

    if pretty_print:
        pretty_execution_status(
            workflow_id=workflow_id,  #resolved_workflow_id,
            workflow_metadata=workflow_metadata,
            do_expand_sub_workflows=expand_subworkflows,
        )
    else:
        print_task_status_summary(workflow_metadata=workflow_metadata)

    return 0


def pretty_execution_status(
        workflow_id: str, workflow_metadata: dict, do_expand_sub_workflows: bool
):
    """
    Prints the workflow summary and calls the task to print formatted workflow status

    :param workflow_id:
    :param workflow_metadata:
    :param do_expand_sub_workflows:
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
        expand_sub_workflows=do_expand_sub_workflows,
    )


def print_workflow_status(
        workflow_metadata: dict, indent: str, expand_sub_workflows: bool
):
    """
    Recursively runs through each task of a workflow metadata and calls task to
    print task status counts
    :param workflow_metadata:
    :param indent:
    :param expand_sub_workflows:
    :return:
    """
    tasks = list(workflow_metadata["calls"].keys())

    for task in tasks:  # for each task in given metadata
        # If task has a key called subworkflowMetadata in its first (zero)
        # element dictionary
        if (
            "subWorkflowMetadata" in workflow_metadata["calls"][task][0]
            and expand_sub_workflows
        ):
            sub_workflow_name = task
            print(f"{indent}SubWorkflow {sub_workflow_name}")

            for i in range(
                len(workflow_metadata["calls"][sub_workflow_name]) - 1
            ):  # For each element in total number of elements in subworkflow list
                sub_workflow_metadata = workflow_metadata["calls"][sub_workflow_name][
                    i
                ]["subWorkflowMetadata"]

                print_workflow_status(
                    workflow_metadata=sub_workflow_metadata,
                    indent=indent + "\t",
                    expand_sub_workflows=expand_sub_workflows,
                )  # Look for additional subworkflows within this subworkflow
        else:
            print_task_status(task, indent, workflow_metadata)


def print_task_status(task: str, indent: str, workflow_metadata: dict):
    """

    :param task:
    :param indent:
    :param workflow_metadata:
    :return:
    """

    shards = workflow_metadata["calls"][task]

    shard_status_summary = get_shard_status_count(shards)

    shards_done = shard_status_summary["Done"] if "Done" in shard_status_summary else 0
    shards_running = shard_status_summary["Running"] if "Running" in shard_status_summary else 0
    shards_failed = shard_status_summary["Failed"] if "Failed" in shard_status_summary else 0
    shards_retried = shard_status_summary["RetryableFailure"] if "RetryableFailure" in shard_status_summary else 0

    # Determine what color to print task print out
    if shards_failed == 0 and shards_running == 0:
        task_status_font = io_utils.TextStatusesColor.TASK_COLOR_SUCCEEDED
    elif shards_failed > 0 and shards_running > 0:
        task_status_font = io_utils.TextStatusesColor.TASK_COLOR_FAILING  # Running but will fail
    elif shards_running > 0:
        task_status_font = io_utils.TextStatusesColor.TASK_COLOR_RUNNING
    else:
        task_status_font = io_utils.TextStatusesColor.TASK_COLOR_FAILED

    print(
        colored(
            f"{indent}{task}\t{shards_running} Running, {shards_done} Done, {shards_retried} Preempted, {shards_failed} Failed",
            color=task_status_font,
        )
    )

    if shards_failed:
        failed_shards = []
        failed_shards_index = []
        sorted_shards = sorted(shards, key=lambda y: y["executionStatus"])
        for status, group in groupby(sorted_shards, lambda x: x["executionStatus"]):
            if status == "Failed":
                failed_shards = list(group)

        for shard in failed_shards:
            failed_shards_index.append(shard["shardIndex"])
        print(
            colored(
                f"{indent}Failed shards: {failed_shards_index}", color=task_status_font
            )  # Maybe place contents of if statment in function and add indentation to printout
        )


def print_task_status_summary(workflow_metadata: dict):
    """
    Prints the status count for each task in a workflow.
    Does NOT run expose subworkflows

    :param workflow_metadata:
    :return:
    """

    workflow_status_summary = {}
    for task in workflow_metadata["calls"]:
        # Method to sort task shards by status (executionStatus)
        shards = workflow_metadata["calls"][task]

        # Add the status counts for this task to dictionary holding other
        # task status counts
        workflow_status_summary[task] = get_shard_status_count(shards)

    io_utils.pretty_print_json(format_json=workflow_status_summary)


def get_shard_status_count(shards: dict) -> dict:
    """
    Count the number of shards for each status type and return as dictionary.
    :param shards: Task shards
    :return:
    """

    sorted_shards = sorted(shards, key=lambda y: y['executionStatus'])
    statuses_count = {}
    for status, group in groupby(sorted_shards, lambda x: x["executionStatus"]):
        statuses_count[status] = len(list(group))

    return statuses_count
