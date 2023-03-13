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
@click.pass_obj
def main(config, workflow_ids, detailed):
    """List workflow outputs."""

    LOGGER.info("list-outputs")

    return_code = 0

    for workflow_id in workflow_ids:
        command_setup_utils.resolve_workflow_id_and_server(
            workflow_id=workflow_id, cromshell_config=config
        )

        if not detailed:
            io_utils.pretty_print_json(format_json=get_workflow_level_outputs(config))
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

    return get_outputs(workflow_metadata)


def get_outputs(workflow_metadata: dict):
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
                    get_outputs(scatter["subWorkflowMetadata"]))
        else:
            output_metadata[call] = []
            for index in index_list:
                output_metadata[call].append(index.get(extract_task_key))

    return output_metadata


def print_task_level_outputs(output_metadata: dict):
    """Print the outputs from the workflow metadata

    Args:
        output_metadata (dict): The output metadata from the workflow
        """
    for call, index_list in output_metadata.items():
        print(call)
        for index in index_list:
            if index is not None:
                io_utils.pretty_print_json(format_json=index)
