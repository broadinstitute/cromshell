import contextlib
import csv
import json
import logging
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from pathlib import PurePath

import click
import requests

from cromshell import log
from cromshell.utilities import cromshellconfig
from cromshell.utilities import http_utils
from cromshell.utilities import io_utils
from cromshell.utilities.io_utils import dead_turtle

LOGGER = logging.getLogger(__name__)


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
    help="ZIP file containing workflow source files that are "
    "used to resolve local imports. This zip bundle will be "
    "unpacked in a sandbox accessible to this workflow.",
)
@click.pass_obj
def main(config, wdl, wdl_json, options_json, dependencies_zip):
    """Submit a workflow and arguments to the Cromwell Server"""

    LOGGER.info("submit")

    validate_input(wdl, wdl_json, options_json, dependencies_zip)

    # Check if Cromwell Server Backend works
    http_utils.assert_can_communicate_with_server(config)

    # Submit workflow to Cromwell Server
    LOGGER.info(f"Submitting job to server: {cromshellconfig.cromwell_server}")
    request_out = submit_workflow_to_server(
        wdl, wdl_json, options_json, dependencies_zip, config
    )

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
        io_utils.log_error_and_raise_exception(
            error_source="Cromshell Server",
            error_source_message=request_out.text,
            short_error_message="Server reports job was not properly submitted.",
        )

    # 2.B If the ID is not an ID, something went wrong:
    if not io_utils.is_workflow_id_valid(workflow_status["id"]):
        log.display_logo(dead_turtle)
        io_utils.log_error_and_raise_exception(
            error_source="Cromshell Server",
            error_source_message=request_out.text,
            short_error_message="Did not get a valid ID back. Something went wrong.",
        )

    # Everything checks out, display success to terminal
    log.display_logo(io_utils.turtle)
    io_utils.pretty_print_json(request_out.text)

    # If we get here, we successfully submitted the job and should track it locally:
    # 1. Create a directory to hold function input files, using server name
    run_directory = Path(config.config_dir).joinpath(
        config.local_folder_name, workflow_status["id"]
    )
    io_utils.create_directory(run_directory)

    # 2. Copy input to run directory
    io_utils.copy_files_to_directory(
        run_directory, [wdl, wdl_json, options_json, dependencies_zip]
    )

    # 3. Update config.submission_file:
    update_submission_file(
        config.cromwell_server, config.submission_file, wdl, workflow_status
    )

    return 0


def validate_input(wdl: str, wdl_json: str, options_json: str, dependencies_zip: str):
    """Asserts files are not empty and if womtool is
    in path validates WDL and WDL input JSON"""

    io_utils.assert_required_file_is_not_empty(wdl, "WDL")
    io_utils.assert_required_file_is_not_empty(wdl_json, "Input JSON")
    io_utils.assert_required_file_is_not_empty(options_json, "Options json")
    io_utils.assert_required_file_is_not_empty(dependencies_zip, "Dependencies Zip")

    # At this point, we should validate our inputs if womtool is in PATH:
    womtool_validate_wdl_and_json(wdl, wdl_json)


def womtool_validate_wdl_and_json(wdl: str, wdl_json: str):
    """If womtool is found in PATH, validates wdl and json"""

    womtool_path = shutil.which("womtool")
    if womtool_path is not None:
        validation_output = subprocess.run(
            [womtool_path, "validate", wdl, "-i", wdl_json], capture_output=True
        )
        if 0 == validation_output.returncode:
            LOGGER.info("WDL and JSON are valid.")
            return 0
        else:
            io_utils.log_error_and_raise_exception(
                error_source="Womtool",
                error_source_message=validation_output.stderr.decode("utf-8"),
                short_error_message="WDL and JSON files do not validate",
            )


def submit_workflow_to_server(wdl, wdl_json, options_json, dependencies_zip, config):
    """Submits workflow and related files to cromwell server"""

    none_context = contextlib.nullcontext()  # Give to file handler if file is None
    # "With" below will open multiple files, since the options_json and dependencies_zip
    # files are optional the "with" statement has conditionals that opens the files
    # only if they are not NONE. To do this none_context is used to pass to the file
    # handler, which avoids errors if optional files are NONE.
    with open(wdl, "rb") as wdl_file, open(wdl_json, "rb") as wdl_json_file, (
        open(options_json, "rb") if options_json is not None else none_context
    ) as options_file, (
        open(dependencies_zip, "rb") if dependencies_zip is not None else none_context
    ) as dependencies_file:

        submission_params = {
            "workflowSource": wdl_file,
            "workflowInputs": wdl_json_file,
        }
        if options_json is not None:
            submission_params["workflowOptions"] = options_file
        if dependencies_zip is not None:
            submission_params["workflowDependencies"] = dependencies_file

        requests_out = requests.post(
            f"{config.cromwell_server}{config.api_string}",
            files=submission_params,
            timeout=5,
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

    with open(submission_file, "a") as f:
        writer = csv.writer(f, delimiter="\t", lineterminator="\n")
        writer.writerow(submission_row)


if __name__ == "__main__":
    main()
