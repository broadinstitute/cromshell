import csv
import json
import logging

import click
import requests
from tabulate import tabulate

import cromshell.utilities.submissions_file_utils
from cromshell.utilities import command_setup_utils, cromshellconfig, http_utils

# from ..status import command as status

LOGGER = logging.getLogger(__name__)


@click.command(name="list")
@click.option(
    "-c",
    "--color",
    is_flag=True,
    default=False,
    help="Color the output by completion status.",
)
@click.option(
    "-u",
    "--update",
    is_flag=True,
    default=False,
    help="Check completion status of all unfinished jobs.",
)
@click.pass_obj
def main(config, color, update):
    """List the status of workflows."""

    LOGGER.info("list")

    # Update the submission database if so requested
    if update:
        update_submission_db(config)

    # Iterate over the submissions text database and print to screen in a pretty way
    with open(cromshellconfig.submission_file_path, "r") as sub_f:
        reader = csv.reader(sub_f, delimiter="\t", lineterminator="\n")
        table_rows = []
        for table_row in reader:
            table_rows.append(format_status(table_row) if color else table_row)

        print(tabulate(table_rows, headers="firstrow", numalign="left"))

    return 0


def update_submission_db(config):
    # Iterate over the submissions text database and update their status
    workflow_ids = []
    with open(cromshellconfig.submission_file_path, "r") as sub_f:
        reader = csv.reader(sub_f, delimiter="\t", lineterminator="\n")
        for table_row in reader:
            if table_row[2] != "RUN_ID" and table_row[4] in [
                "Submitted",
                "Running",
                "DOOMED",
            ]:
                workflow_ids.append(table_row[2])

    for workflow_id in workflow_ids:
        command_setup_utils.resolve_workflow_id_and_server(
            workflow_id=workflow_id, cromshell_config=config
        )

        # Request workflow status
        request_out = requests.get(
            f"{config.cromwell_api_workflow_id}/status",
            timeout=config.requests_connect_timeout,
            verify=config.requests_verify_certs,
            headers=http_utils.generate_headers(config),
        )

        workflow_status_description = json.loads(request_out.content)

        # Hold our status string here
        workflow_status = workflow_status_description["status"]

        # Update config.submission_file:
        cromshell.utilities.submissions_file_utils.update_row_values_in_submission_db(
            workflow_database_path=config.submission_file_path,
            workflow_id=workflow_id,
            column_to_update="STATUS",
            update_value=workflow_status,
        )


def format_status(table_row):
    colorful_status = {
        "Failed": "\033[1;37;41mFailed\033[0m",
        "DOOMED": "\033[1;31;47mDOOMED\033[0m",
        "Succeeded": "\033[1;30;42mSucceeded\033[0m",
        "Running": "\033[0;30;46mRunning\033[0m",
        "Aborted": "\033[0;30;43mAborted\033[0m",
    }

    status_column = -1 if table_row[-1] in colorful_status else -2

    if table_row[status_column] in colorful_status:
        table_row[status_column] = colorful_status[table_row[status_column]]

    return table_row
