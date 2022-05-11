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


def update_submission_db(submission_file_path: Union[str, Path]) -> bool:
    """Read the first line of the submission database. If not tab-delimited (old format)
    then update the database so it is tab-delimited."""

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
