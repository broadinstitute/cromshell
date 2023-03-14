import logging

import click
import requests

import cromshell.utilities.http_utils as http_utils
import cromshell.utilities.io_utils as io_utils
from cromshell.utilities import command_setup_utils
from cromshell.metadata import command as metadata_command

LOGGER = logging.getLogger(__name__)


@click.command(name="list-outputs")
@click.argument("workflow_ids", required=True, nargs=-1)
@click.option(
    "-d",
    "--detailed",
    is_flag=True,
    default=False,
    help="Get the output for a workflow at the task level",
)
@click.option(
    "-j",
    "--json-summary",
    is_flag=True,
    default=False,
    help="Print a json summary of the task outputs, including non file types.",
)
@click.pass_obj
def main(config, workflow_ids, detailed, json_summary):
    """List workflow outputs."""

    LOGGER.info("list-outputs")

    return_code = 0

    for workflow_id in workflow_ids:
        command_setup_utils.resolve_workflow_id_and_server(
            workflow_id=workflow_id, cromshell_config=config
        )

        if not detailed:
            if json_summary:
                io_utils.pretty_print_json(format_json=get_workflow_level_outputs(config).get("outputs"))
            else:
                print_workflow_level_outputs(get_workflow_level_outputs(config))
        else:
            if json_summary:
                io_utils.pretty_print_json(format_json=get_task_level_outputs(config))
            else:
                print_task_level_outputs(get_task_level_outputs(config))

    return return_code


def get_workflow_level_outputs(config) -> dict:
    """Get the workflow level outputs from the workflow outputs"""

    requests_out = requests.get(
        f"{config.cromwell_api_workflow_id}/outputs",
        timeout=config.requests_connect_timeout,
        verify=config.requests_verify_certs,
        headers=http_utils.generate_headers(config),
    )

    if requests_out.ok:
        return requests_out.json()
    else:

        http_utils.check_http_request_status_code(
            short_error_message="Failed to retrieve workflow outputs.",
            response=requests_out,
            # Raising exception is set false to allow
            # command to retrieve outputs of remaining workflows.
            raise_exception=False,
        )


def get_task_level_outputs(config):
    """Get the task level outputs from the workflow metadata

    Args:
        config (dict): The cromshell config object
        """
    # Get metadata
    formatted_metadata_parameter = metadata_command.format_metadata_params(
        list_of_keys=config.METADATA_KEYS_TO_OMIT,
        exclude_keys=True,
        expand_subworkflows=True,
    )

    workflow_metadata = metadata_command.get_workflow_metadata(
        meta_params=formatted_metadata_parameter,
        api_workflow_id=config.cromwell_api_workflow_id,
        timeout=config.requests_connect_timeout,
        verify_certs=config.requests_verify_certs,
        headers=http_utils.generate_headers(config),
    )

    return filer_outputs_from_workflow_metadata(workflow_metadata)


def filer_outputs_from_workflow_metadata(workflow_metadata: dict) -> dict:
    """Get the outputs from the workflow metadata

    Args:
        workflow_metadata (dict): The workflow metadata
        """
    calls_metadata = workflow_metadata["calls"]
    output_metadata = {}
    extract_task_key = "outputs"

    for call, index_list in calls_metadata.items():
        if "subWorkflowMetadata" in calls_metadata[call][0]:
            output_metadata[call] = []
            for scatter in calls_metadata[call]:
                output_metadata[call].append(
                    filer_outputs_from_workflow_metadata(scatter["subWorkflowMetadata"]))
        else:
            output_metadata[call] = []
            for index in index_list:
                output_metadata[call].append(index.get(extract_task_key))

    return output_metadata


def print_task_level_outputs(output_metadata: dict) -> None:
    """Print the outputs from the workflow metadata
    output_metadata: {call_name:[index1{output_name: outputvalue}, index2{...}, ...], call_name:[], ...}

    Args:
        output_metadata (dict): The output metadata from the workflow
        """
    for call, index_list in output_metadata.items():
        print(call)
        for call_index in index_list:
            if call_index is not None:
                for task_output_name, task_output_value in call_index.items():
                    if isinstance(task_output_value, str):
                        print_task_name_and_file(task_output_name, task_output_value)
                    elif isinstance(task_output_value, list):
                        for task_value in task_output_value:
                            print_task_name_and_file(task_output_name, task_value)


def print_workflow_level_outputs(workflow_outputs_json: dict) -> None:
    """Print the workflow level outputs from the workflow outputs"""
    workflow_outputs = workflow_outputs_json["outputs"]

    for workflow_output_name, workflow_output_value in workflow_outputs.items():
        if isinstance(workflow_output_value, str):
            print_task_name_and_file(workflow_output_name, workflow_output_value, indent=False)
        elif isinstance(workflow_output_value, list):
            for task_value in workflow_output_value:
                print_task_name_and_file(workflow_output_name, task_value, indent=False)


def print_task_name_and_file(
        task_output_name: str, task_output_value: str, indent: bool = True
) -> None:
    """Print the task name and the file name"""

    i = "\t" if indent else ""

    if isinstance(task_output_value, str):
        if is_path_or_url_like(task_output_value):
            print(f"{i}{task_output_name}: {task_output_value}")


def is_path_or_url_like(in_string: str) -> bool:
    """Check if the string is a path or url"""

    if in_string.startswith("gs://") or in_string.startswith(
            "/") or in_string.startswith("http://") or in_string.startswith("https://"):
        return True
    else:
        return False
