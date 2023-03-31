import logging

import click
import requests

import cromshell.utilities.http_utils as http_utils
import cromshell.utilities.io_utils as io_utils
from cromshell.metadata import command as metadata_command
from cromshell.utilities import command_setup_utils

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
    help="Print a json summary of outputs, including non-file types.",
)
@click.pass_obj
def main(config, workflow_ids, detailed, json_summary):
    """List all output files produced by a workflow."""

    LOGGER.info("list-outputs")

    return_code = 0

    for workflow_id in workflow_ids:
        command_setup_utils.resolve_workflow_id_and_server(
            workflow_id=workflow_id, cromshell_config=config
        )

        if not detailed:
            workflow_outputs = get_workflow_level_outputs(config).get("outputs")

            if json_summary:
                io_utils.pretty_print_json(format_json=workflow_outputs)
            else:
                print_file_like_value_in_dict(
                    outputs_metadata=workflow_outputs,
                    indent=False,
                )
        else:
            task_outputs = get_task_level_outputs(config)

            if json_summary:
                io_utils.pretty_print_json(format_json=task_outputs)
            else:
                print_task_level_outputs(task_outputs)

    return return_code


def get_workflow_level_outputs(config) -> dict:
    """Get the workflow level outputs from the workflow outputs

    Args:
        config (dict): The cromshell config object
    """

    requests_out = requests.get(
        f"{config.cromwell_api_workflow_id}/outputs",
        timeout=config.requests_connect_timeout,
        verify=config.requests_verify_certs,
        headers=http_utils.generate_headers(config),
    )

    if requests_out.ok:
        check_for_empty_output(requests_out.json().get("outputs"), config.workflow_id)
        return requests_out.json()
    else:
        http_utils.check_http_request_status_code(
            short_error_message="Failed to retrieve outputs for "
                                f"workflow: {config.workflow_id}",
            response=requests_out,
            # Raising exception is set false to allow
            # command to retrieve outputs of remaining workflows.
            raise_exception=False,
        )


def get_task_level_outputs(config) -> dict:
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

    return filter_outputs_from_workflow_metadata(workflow_metadata)


def filter_outputs_from_workflow_metadata(workflow_metadata: dict) -> dict:
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
                    filter_outputs_from_workflow_metadata(
                        scatter["subWorkflowMetadata"]
                    )
                )
        else:
            output_metadata[call] = []
            for index in index_list:
                output_metadata[call].append(index.get(extract_task_key))

    check_for_empty_output(output_metadata, workflow_metadata["id"])

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
                print_file_like_value_in_dict(outputs_metadata=call_index, indent=True)


def print_file_like_value_in_dict(outputs_metadata: dict, indent: bool) -> None:
    """Print the file like values in the output metadata dictionary

    Args:
        outputs_metadata (dict): The output metadata
        indent (bool): Whether to indent the output
    """

    for output_name, output_value in outputs_metadata.items():
        if isinstance(output_value, str):
            print_output_name_and_file(output_name, output_value, indent=indent)
        elif isinstance(output_value, list):
            for output_value_item in output_value:
                print_output_name_and_file(
                    output_name, output_value_item, indent=indent
                )


def print_output_name_and_file(
    output_name: str, output_value: str, indent: bool = True
) -> None:
    """Print the task name and the file name

    Args:
        output_name (str): The task output name
        output_value (str): The task output value
        indent (bool): Whether to indent the output"""

    i = "\t" if indent else ""

    if isinstance(output_value, str):
        if is_path_or_url_like(output_value):
            print(f"{i}{output_name}: {output_value}")


def is_path_or_url_like(in_string: str) -> bool:
    """Check if the string is a path or url

    Args:
        in_string (str): The string to check for path or url like-ness
    """
    if (
        in_string.startswith("gs://")
        or in_string.startswith("/")
        or in_string.startswith("http://")
        or in_string.startswith("https://")
    ):
        return True
    else:
        return False


def check_for_empty_output(workflow_outputs: dict, workflow_id: str) -> None:
    """Check if the workflow outputs are empty

    Args:
        cromwell_outputs (dict): Dictionary of workflow outputs
        :param workflow_id: The workflow id
    """
    if not workflow_outputs:
        LOGGER.error(f"No outputs found for workflow: {workflow_id}")
        raise Exception(f"No outputs found for workflow: {workflow_id}")
