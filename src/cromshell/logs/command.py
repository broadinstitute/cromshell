import logging
import os

import click
import gcsfs
from termcolor import colored

from cromshell.metadata import command as metadata_command
from cromshell.utilities.io_utils import get_color_for_status_key

LOGGER = logging.getLogger(__name__)


@click.command(name="logs")
@click.argument("workflow_id")
@click.option(
    "-s",
    "--status",
    default="Failed",
    help="Return a list with links to the logs with the indicated status. "
    "Separate multiple keys by comma or use 'ALL' to print all logs. "
    "Some standard Cromwell status options are 'ALL', 'Done', 'RetryableFailure', 'Running', and 'Failed'.",
)
@click.option(
    "-p",
    "--print-logs",
    is_flag=True,
    default=False,
    help="Print the contents of the logs to stdout if true. "
    "Note: This assumes GCS bucket logs with default permissions otherwise this may not work",
)
@click.option(
    "-des",
    "--dont-expand-subworkflows",
    is_flag=True,
    default=False,
    help="Do not expand subworkflow info in metadata",
)
@click.pass_obj
def main(
    config,
    workflow_id: str,
    status: list,
    dont_expand_subworkflows: bool,
    print_logs: bool,
):
    """Get a subset of the workflow metadata."""

    LOGGER.info("logs")

    # If no keys were provided then set key_param to empty else
    # strip trailing comma from keys and split keys by comma
    status_param = (
        ["ALL"]
        if "ALL".lower() in status.lower()
        else str(status).strip(",").split(",")
    )

    metadata_command.check_cromwell_server(config=config, workflow_id=workflow_id)

    LOGGER.info("Status keys set to %s", status_param)

    # To grab the logs we only need a subset of the metadata from the server
    obtain_and_print_logs(
        config=config,
        metadata_param=[
            "id",
            "executionStatus",
            "backendLogs",
            "subWorkflowMetadata",
            "subWorkflowId",
        ],
        status_params=status_param,
        dont_expand_subworkflows=dont_expand_subworkflows,
        print_logs=print_logs,
    )

    return 0


def obtain_and_print_logs(
    config,
    metadata_param: list,
    print_logs: bool,
    status_params: list,
    dont_expand_subworkflows: bool,
):
    """Format metadata parameters and obtains metadata from cromwell server"""

    # Combine keys and flags into a dictionary
    formatted_metadata_parameter = metadata_command.format_metadata_params(
        list_of_keys=metadata_param,
        exclude_keys=False,
        expand_subworkflows=not dont_expand_subworkflows,  # Invert variable
    )

    # Request workflow metadata
    workflow_status_json = metadata_command.get_workflow_metadata(
        meta_params=formatted_metadata_parameter,
        api_workflow_id=config.cromwell_api_workflow_id,
        timeout=config.requests_connect_timeout,
        verify_certs=config.requests_verify_certs,
    )

    # Parse the metadata for logs and print them to the output
    found_logs = print_workflow_logs(
        workflow_metadata=workflow_status_json,
        indent="",
        expand_sub_workflows=not dont_expand_subworkflows,
        status_keys=status_params,
        cat_logs=print_logs,
    )

    if not found_logs:
        print(
            f"No logs with status {status_params} found for workflow, try adding the argument '-s ALL' to list logs with any status"
        )


def print_workflow_logs(
    workflow_metadata: dict,
    indent: str,
    expand_sub_workflows: bool,
    status_keys: list,
    cat_logs: bool,
) -> bool:
    """
    Recursively runs through each task of a workflow metadata and calls function to
    call out to the helper in order to print found logs
    :param workflow_metadata: Metadata of the workflow to process
    :param indent: Indent string given as "\t", used to indent print out
    :param expand_sub_workflows:  Boolean, whether or not to print subworkflows
    :return: true if any logs matching the parameters were found
    """
    did_print = False

    tasks = list(workflow_metadata["calls"].keys())

    for task in tasks:  # For each task in given metadata
        # If task has a key called 'subworkflowMetadata' in its first (zero) element
        # (shard) and expand_sub_workflow parameter is set to true then rerun this
        # function on that subworkflow
        if (
            "subWorkflowMetadata" in workflow_metadata["calls"][task][0]
            and expand_sub_workflows
        ):
            sub_workflow_name = task
            task_shards = workflow_metadata["calls"][sub_workflow_name]
            print(f"{indent}SubWorkflow {sub_workflow_name}")

            # For each element in total number of subworkflow calls get the subworkflow
            # metadata. This loop will go through each shard if task is scattered
            for i in range(len(task_shards) - 1):
                sub_workflow_metadata = task_shards[i]["subWorkflowMetadata"]

                print_workflow_logs(
                    workflow_metadata=sub_workflow_metadata,
                    indent=indent + "\t",
                    expand_sub_workflows=expand_sub_workflows,
                    status_keys=status_keys,
                    cat_logs=cat_logs,
                )

        # If no subworkflow is found then print status summary for the task
        else:
            did_print = (
                print_task_logs(task, indent, workflow_metadata, status_keys, cat_logs)
                or did_print
            )

    return did_print


def print_task_logs(
    task: str,
    indent: str,
    workflow_metadata: dict,
    status_keys: list,
    cat_logs: bool,
) -> bool:
    """
    Prints the backend logs from the workflow
    :param task: Name of the task
    :param indent: Indent string given as a string of "\t" characters, used to indent print out
    :param workflow_metadata: Metadata of the workflow to process
    :param cat_logs: Will use GCS to attempt to print the logs
    :return: true if any logs were printed
    """

    did_print = False

    shard_list = workflow_metadata["calls"][task]

    sharded = workflow_metadata["calls"][task][0]["shardIndex"] != -1

    for i in range(len(shard_list)):

        status = shard_list[i]["executionStatus"]
        if "ALL" in status_keys or status in status_keys:
            task_status_font = get_color_for_status_key(status)

            shardstring = (
                "" if not sharded else "-shard-" + str(shard_list[i]["shardIndex"])
            )
            logs = shard_list[i]["backendLogs"]["log"]
            if cat_logs:
                print(
                    colored(
                        f"\n\n\n{'=' * os.get_terminal_size().columns }\n{indent}{task}{shardstring}:\t{status}\t {logs}\n{'=' * os.get_terminal_size().columns }",
                        color=task_status_font,
                    )
                )
                fs = gcsfs.GCSFileSystem()
                if fs.exists(logs):
                    with fs.open(logs, "r") as f:
                        print(f.read())
                else:
                    print(f"Unable to locate logs at {logs}.")

            else:
                print(
                    colored(
                        f"{indent}{task}{shardstring}:\t{status}\t {logs}",
                        color=task_status_font,
                    )
                )
            did_print = True
    return did_print


if __name__ == "__main__":
    main()
