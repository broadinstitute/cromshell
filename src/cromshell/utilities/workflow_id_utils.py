import csv
import logging

from cromshell.utilities import cromshellconfig, io_utils
from cromshell.utilities.cromshellconfig import (
    ImmutableSubmissionFileHeader,
    MutableSubmissionFileHeader,
)

LOGGER = logging.getLogger(__name__)


def resolve_workflow_id(cromshell_input: str, submission_file_path: str) -> str:
    """
    Uses input provided by user when running cromshell to identify and return the
    workflow id from cromshell's submission file
    :param cromshell_input: User's provided input (digit or alias) in cromshell command
    :param submission_file_path: path to all.workflow.database.tsv
    :return: workflow id
    """
    if io_utils.is_workflow_id_valid(cromshell_input):
        return cromshell_input
    elif cromshell_input.lstrip("-").isdigit():
        return obtain_workflow_id_using_digit(
            relative_id=int(cromshell_input),
            submission_file_path=submission_file_path,
        )
    else:
        return obtain_workflow_id_using_alias(
            alias_name=cromshell_input,
            submission_file_path=submission_file_path,
        )


def obtain_workflow_id_using_digit(relative_id: int, submission_file_path: str) -> str:
    """
    Get workflow id from submission file using relative_id.
    :param relative_id: digit representative of the row of the desired
    row from submission file.
    :param submission_file_path: path to all.workflow.database.tsv
    :return: workflow id
    """
    LOGGER.info("Get workflow id from submission file using relative_id.")
    if relative_id == 0:
        LOGGER.error("Relative workflow id must be a non zero integer")
        raise ValueError("Relative workflow id must be a non zero integer")

    with open(submission_file_path, "r") as csv_file:

        reader = csv.DictReader(csv_file, delimiter="\t")
        mycsv = list(reader)
        total_rows = len(mycsv)

    if abs(relative_id) > total_rows:
        LOGGER.error(
            "The relative id value '%i' is greater than the total rows in "
            "submission file is : %i",
            relative_id,
            total_rows,
        )
        raise ValueError(
            f"Unable to use relative id value '{relative_id}' to obtain workflow id"
        )

    row_index = (
        relative_id if relative_id < 0 else relative_id - 1
    )  # Subtracting 1 to account for row shift when dealing with list index

    return mycsv[row_index][ImmutableSubmissionFileHeader.Run_ID.value]


def obtain_workflow_id_using_alias(alias_name: str, submission_file_path: str) -> str:
    """
    Get workflow id from submission file using alias
    :param alias_name: alias to search in submission file
    :param submission_file_path: path to all.workflow.database.tsv
    :return: workflow id
    """
    LOGGER.info("Get workflow id from submission file using alias.")
    with open(submission_file_path, "r") as csv_file:
        reader = csv.DictReader(csv_file, delimiter="\t")
        for row in reader:
            if row[MutableSubmissionFileHeader.Alias.value] == alias_name:
                return row[ImmutableSubmissionFileHeader.Run_ID.value]

        LOGGER.error(
            "Unable to find alias '%s' in submission file '%s'",
            alias_name,
            cromshellconfig.submission_file_path,
        )
        raise ValueError(f"Unable to find alias {alias_name} in submission file")


def workflow_id_exists(workflow_id: str, submission_file) -> bool:
    """
    Check if workflow ID exists in submission file.
    :param workflow_id: Hexadecimal identifier of workflow
    :param submission_file: Path to cromshell submission file
    :return: boolean indicating whether workflow id exists in submission file
    """
    with open(submission_file, "r") as csv_file:
        reader = csv.DictReader(csv_file, delimiter="\t")
        for row in reader:
            if row[ImmutableSubmissionFileHeader.Run_ID.value] == workflow_id:
                return True
        return False
