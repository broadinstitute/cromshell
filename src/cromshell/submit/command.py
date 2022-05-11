import contextlib
import csv
import json
import logging
from datetime import datetime
from pathlib import Path, PurePath

import click
import requests
from requests import Response

from cromshell import log
from cromshell.utilities import cromshellconfig, http_utils, io_utils
from cromshell.utilities.io_utils import dead_turtle

LOGGER = logging.getLogger(__name__)


class ValidationError(Exception):
    """Raised when input WDL or JSON does not pass Womtool Validation"""


class WorkflowIDError(Exception):
    """Raised when Workflow ID does not meet the correct format"""


class WorkflowStatusError(Exception):
    """Raised when Workflow Status of a recently submitted workflow
    is not 'Submitted'"""


@click.command(name="submit")
@click.argument("wdl", type=click.Path(exists=True), required=True)
@click.argument("wdl_json", type=click.Path(exists=True), required=True)
@click.option(
    "-op",
    "--options-json",
    type=click.Path(exists=True),
    required=False,
    help="JSON file containing configuration options "
    "for the execution of the workflow.",
)
@click.option(
    "-d",
    "--dependencies-zip",
    type=click.Path(exists=True),
    required=False,
    help="ZIP file or directory containing workflow source files that are "
    "used to resolve local imports. This zip bundle will be "
    "unpacked in a sandbox accessible to this workflow.",
)
@click.option(
    "-n",
    "--no-validation",
    is_flag=True,
    default=False,
    help="Do not check womtool for validation before submitting.",
)
@click.pass_obj
def main(config, wdl, wdl_json, options_json, dependencies_zip, no_validation):
    """Submit a workflow and arguments to the Cromwell Server"""

    LOGGER.info("submit")

    http_utils.assert_can_communicate_with_server(config)

    if no_validation:
        LOGGER.info("Skipping WDL validation")
    else:
        validate_input(wdl, wdl_json, options_json, dependencies_zip, config)

    LOGGER.info("Submitting job to server: %s", cromshellconfig.cromwell_server)
    request_out = submit_workflow_to_server(
        wdl, wdl_json, options_json, dependencies_zip, config
    )

    # TODO: Refactor these post submission checks into a single checking function
    # Check to make sure that we actually submitted the job correctly
    # 1. Check for any initial failure by server to accept the job.
    http_utils.check_http_request_status_code(
        short_error_message="Failed to Submit Workflow", response=request_out
    )

    # 2. Check messages from server for workflow problems.
    # Get our workflow status and job ID:
    workflow_status = json.loads(request_out.content)

    # 2.A If the status is not `Submitted`, something went wrong:
    if workflow_status["status"] != "Submitted":
        log.display_logo(dead_turtle)

        LOGGER.error("Error: Server reports job was not properly submitted.")
        LOGGER.error("Cromshell Server Message: %s", request_out.text)
        raise WorkflowStatusError(
            f"Error: Server reports job was not properly submitted.\n"
            f"Cromshell Server Message: {request_out.text}"
        )

    # 2.B If the ID is not an ID, something went wrong:
    if not io_utils.is_workflow_id_valid(workflow_status["id"]):
        log.display_logo(dead_turtle)

        LOGGER.error("Error: Did not get a valid ID back. Something went wrong.")
        LOGGER.error("Cromshell Server Message: %s", request_out.text)
        raise WorkflowIDError(
            f"Error: Did not get a valid ID back. Something went wrong.\n"
            f"Cromshell Server Message: {request_out.text}"
        )

    # Everything checks out, display success to terminal
    log.display_logo(io_utils.turtle)
    io_utils.pretty_print_json(request_out.json())

    # TODO: Refactor these file manipulations into its own "cleanup" function?
    # If we get here, we successfully submitted the job and should track it locally:
    # 1. Create a directory to hold function input files, using server name
    server_folder_name = config.get_local_folder_name()
    run_directory = Path(config.config_dir).joinpath(
        server_folder_name, workflow_status["id"]
    )
    io_utils.create_directory(run_directory)

    # 2. Copy input to run directory
    io_utils.copy_files_to_directory(
        run_directory, [wdl, wdl_json, options_json, dependencies_zip]
    )

    # 3. Update config.submission_file_path:
    update_submission_file(
        config.cromwell_server, config.submission_file_path, wdl, workflow_status
    )

    return 0


def validate_input(
    wdl: str,
    wdl_json: str,
    options_json: str,
    dependencies_zip: str,
    config: cromshellconfig,
) -> None:
    """Asserts files are not empty and if womtool is
    in path validates WDL and WDL input JSON"""

    io_utils.assert_path_is_not_empty(wdl, "WDL")
    io_utils.assert_path_is_not_empty(wdl_json, "Input JSON")
    if options_json is not None:
        io_utils.assert_path_is_not_empty(options_json, "Options json")
    if dependencies_zip is not None:
        io_utils.assert_path_is_not_empty(dependencies_zip, "Dependencies Zip")

    if dependencies_zip is None:
        womtool_validate_wdl_and_json(wdl, wdl_json, config)
    else:
        # See: https://github.com/broadinstitute/cromshell/issues/139
        LOGGER.info("Skipping validation of WDL plus a dependencies zip")


def womtool_validate_wdl_and_json(
    wdl: str, wdl_json: str, config: cromshellconfig
) -> None:
    """Validates WDL and input JSON using the Cromwell server's Womtool REST API"""

    LOGGER.info("Validating WDL with with server: %s", config.cromwell_server)
    request_out = womtool_validate_to_server(wdl, wdl_json, config)

    http_utils.check_http_request_status_code(
        short_error_message="Failed to Validate Workflow", response=request_out
    )

    validate_status = json.loads(request_out.content)

    if not validate_status["valid"]:
        log.display_logo(dead_turtle)

        LOGGER.error("Error: Server reports workflow was not valid.")
        raise ValidationError(
            "Error: Server reports workflow was not valid.\n"
            + ("\n".join(validate_status["errors"]))
        )


def womtool_validate_to_server(
    wdl: str, wdl_json: str, config: cromshellconfig
) -> Response:
    with open(wdl, "rb") as wdl_file, open(wdl_json, "rb") as wdl_json_file:
        submission_params = {
            "workflowSource": wdl_file,
            "workflowInputs": wdl_json_file,
        }

        requests_out = requests.post(
            f"{config.get_womtool_api()}/describe",
            files=submission_params,
            timeout=config.requests_connect_timeout,
            verify=config.requests_verify_certs,
            headers=http_utils.generate_headers(config),
        )

        return requests_out


def submit_workflow_to_server(wdl, wdl_json, options_json, dependencies_zip, config):
    """Submits workflow and related files to cromwell server"""

    none_context = contextlib.nullcontext()  # Give to file handler if file is None
    # "With" below will open multiple files, since the options_json and dependencies_zip
    # files are optional the "with" statement has conditionals that opens the files
    # only if they are not NONE. To do this none_context is used to pass to the file
    # handler, which avoids errors if optional files are NONE.
    with open(wdl, "rb") as wdl_file, open(wdl_json, "rb") as wdl_json_file, (
        open(options_json, "rb") if options_json is not None else none_context
    ) as options_file, (io_utils.open_or_zip(dependencies_zip)) as dependencies_file:

        submission_params = {
            "workflowSource": wdl_file,
            "workflowInputs": wdl_json_file,
        }
        if options_json is not None:
            submission_params["workflowOptions"] = options_file
        if dependencies_zip is not None:
            submission_params["workflowDependencies"] = dependencies_file

        requests_out = requests.post(
            f"{config.get_cromwell_api()}",
            files=submission_params,
            timeout=config.requests_connect_timeout,
            verify=config.requests_verify_certs,
            headers=http_utils.generate_headers(config),
        )

        return requests_out


def update_submission_file(
    cromwell_server: str, submission_file: str, wdl: str, workflow_status: dict
):
    """Update the submission file with recently submitted job"""

    submission_row = [
        datetime.now().strftime("%Y%m%d_%H%M%S"),
        cromwell_server,
        workflow_status["id"],
        PurePath(wdl).name,
        workflow_status["status"],
        "",  # Place holder for Alias column
    ]

    with open(submission_file, "a") as sub_f:
        writer = csv.writer(sub_f, delimiter="\t", lineterminator="\n")
        writer.writerow(submission_row)


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
