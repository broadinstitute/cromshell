import csv
import logging
import shutil
from datetime import date
from enum import Enum
from pathlib import Path
from typing import Union

LOGGER = logging.getLogger(__name__)


class WorkflowDatabaseColumns(Enum):
    """Enum holding mutable and immutable all_workflow_database.tsv column headers"""

    # For loop gets the subclasses in WorkflowDatabaseColumns enum
    # (MutableSubmissionFileHeader and IMMutableSubmissionFileHeader),
    # then get_database_columns function call is used to get the
    # values for each subclass. Resulting in a list of lists.
    @classmethod
    def get_submission_file_headers(cls):
        return sum(  # Sum flattens list of lists in to list
            [sub_cls._get_database_columns() for sub_cls in cls.__subclasses__()],
            [],
        )


# Immutable class needs to be placed before Mutable class, this is to
# have the headers be listed correctly when creating a submission file.
class ImmutableSubmissionFileHeader(WorkflowDatabaseColumns):
    Date = "DATE"
    Cromwell_Server = "CROMWELL_SERVER"
    Run_ID = "RUN_ID"
    WDL_Name = "WDL_NAME"

    @classmethod
    def _get_database_columns(cls):
        return [key.value for key in cls]


class MutableSubmissionFileHeader(WorkflowDatabaseColumns):
    Status = "STATUS"
    Alias = "ALIAS"

    @classmethod
    def _get_database_columns(cls):
        return [key.value for key in cls]


def update_submission_db_format(submission_file_path: Union[str, Path]) -> bool:
    """Read the first line of the submission database. If not tab-delimited (old format)
    then update the database to tab-delimited."""

    old_format = False

    with open(submission_file_path, "r") as f:
        first_line = f.readline()
        if "\t" not in first_line:
            old_format = True

    if old_format:
        LOGGER.info(f"Detected an old database format at {submission_file_path}")
        backup_filename = (
            submission_file_path + "." + str(date.today()).replace("-", "") + ".bak"
        )
        shutil.copy(src=submission_file_path, dst=backup_filename)
        LOGGER.info(f"Backed up old database at {backup_filename}")
        with open(submission_file_path, "r") as f:
            entire_file = f.read()
        with open(submission_file_path + ".tmp", "w") as f:
            f.write(entire_file.replace(" ", "\t"))
        shutil.move(src=submission_file_path + ".tmp", dst=submission_file_path)
        LOGGER.info(
            f"Updated database at {submission_file_path} to tab-delimited format"
        )

    return old_format  # for tests


def update_row_values_in_submission_db(
    workflow_database_path: str,
    workflow_id: str,
    column_to_update: str,
    update_value: str,
    fields: list = WorkflowDatabaseColumns.get_submission_file_headers(),
) -> None:
    """
    Updates the all_workflow_database_tsv for a given workflow_id and column
    :param workflow_database_path: Path to all_workflow_database tsv file
    :param workflow_id: Hexadecimal identifier of workflow submission
    :param column_to_update:["STATUS", "ALIAS"]
    :param update_value: Value of the cell to update
    :param fields: submission db column name
    :return:
    """

    mutable_columns = [column.value for column in MutableSubmissionFileHeader]
    if column_to_update not in mutable_columns:
        raise KeyError(
            f"Invalid column_to_update: '{column_to_update}'. "
            f"Expected one of: '{mutable_columns}'"
        )

    import tempfile

    tmp = tempfile.NamedTemporaryFile(delete=False)

    # Update row in temp file:
    with open(workflow_database_path, "r") as tsv_file, open(
        tmp.name, "w"
    ) as tempfile_tsv:
        reader = csv.DictReader(tsv_file, delimiter="\t", fieldnames=fields)
        writer = csv.DictWriter(tempfile_tsv, delimiter="\t", fieldnames=fields)
        for row in reader:
            if row["RUN_ID"] == workflow_id:
                row[column_to_update] = update_value
            writer.writerow(row)

    # copy over submission tsv with tempfile
    shutil.move(tmp.name, workflow_database_path)
    tmp.close()
