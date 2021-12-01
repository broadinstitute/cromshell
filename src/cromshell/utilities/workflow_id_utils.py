import csv
import logging

from cromshell.utilities import cromshellconfig, io_utils

LOGGER = logging.getLogger(__name__)


def resolve_workflow_id(cromshell_input: str) -> str:
    if io_utils.is_workflow_id_valid(cromshell_input):
        return cromshell_input
    elif cromshell_input.strip("-").isnumeric():
        return obtain_workflow_id_using_digit(int(cromshell_input))
    else:
        return obtain_workflow_id_using_alias(cromshell_input)


def obtain_workflow_id_using_digit(relative_id: int) -> str:
    """Get workflow id from submission file using relative_id."""
    LOGGER.info("Get workflow id from submission file using relative_id.")
    with open(cromshellconfig.submission_file_path, "r") as csv_file:
        reader = csv.DictReader(csv_file, delimiter="\t")
        total_lines = len(list(reader))
        csv_file.seek(0)  # reset file handler after obtaining total lines

        # If relative id is 0 then use last row
        if relative_id == 0:
            row_index = total_lines
        else:
            row_index = (
                relative_id if relative_id > 0 else total_lines - (abs(relative_id) - 1)
            )

        for i, row in enumerate(reader):
            if i == row_index:
                return row["RUN_ID"]

        # If workflow id wasn't found in previous line then send error
        LOGGER.error(
            "Unable to use relative id value '%i' to obtain workflow id. The total rows"
            " in submission file is : %i, relative id is most likely output of bounds,",
            relative_id,
            total_lines,
        )
        raise ValueError(
            f"Unable to use relative id value '{relative_id}' to obtain workflow id"
        )


def obtain_workflow_id_using_alias(alias_name: str) -> str:
    """Get workflow id from submission file using alias"""
    LOGGER.info("Get workflow id from submission file using alias.")
    with open(cromshellconfig.submission_file_path, "r") as csv_file:
        reader = csv.DictReader(csv_file, delimiter="\t")
        for row in reader:
            if row["ALIAS"] == alias_name:
                return row["RUN_ID"]

        LOGGER.error(
            "Unable to find alias '%s' in submission file '%s'",
            alias_name,
            cromshellconfig.submission_file_path,
        )
        raise ValueError(f"Unable to find alias {alias_name} in submission file")


def workflow_id_exists(workflow_id: str, submission_file) -> bool:
    """Check if workflow ID exists in submission file."""
    with open(submission_file, "r") as csv_file:
        reader = csv.DictReader(csv_file, delimiter="\t")
        for row in reader:
            if row["RUN_ID"] == workflow_id:
                return True
        return False
