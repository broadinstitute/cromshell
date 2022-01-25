import csv
import logging

from cromshell.utilities import cromshellconfig, io_utils

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
    elif cromshell_input.strip("-").isdigit():
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
    # If relative id is 0 then use last row
    if relative_id == 0:
        LOGGER.error("Relative workflow id must be a non zero integer")
        raise ValueError("Relative workflow id must be a non zero integer")

    with open(submission_file_path, "r") as csv_file:

        reader = csv.DictReader(csv_file, delimiter="\t")
        total_rows = len(list(reader))
        csv_file.seek(0)  # reset file handler after obtaining total lines

        row_index = (
            relative_id if relative_id > 0 else (total_rows - abs(relative_id) + 1)
        )  # Adding 1 to account for row shift

        if relative_id > total_rows:
            LOGGER.error(
                "The relative id value '%i' is greater than the total rows in "
                "submission file is : %i",
                relative_id,
                total_rows,
            )
            raise ValueError(
                f"Unable to use relative id value '{relative_id}' to obtain workflow id"
            )

        for i, row in enumerate(reader):
            if i == row_index:
                return row["RUN_ID"]

        # If workflow id wasn't found in previous line then send error
        LOGGER.error(
            "Unable to use relative id value '%i' to obtain workflow id. The total rows"
            " in submission file is : %i",
            relative_id,
            total_rows,
        )
        raise ValueError(
            f"Unable to use relative id value '{relative_id}' to obtain workflow id"
        )


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
            if row["ALIAS"] == alias_name:
                return row["RUN_ID"]

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
            if row["RUN_ID"] == workflow_id:
                return True
        return False
