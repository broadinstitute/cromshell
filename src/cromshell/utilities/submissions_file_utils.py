from enum import Enum


class WorkflowDatabaseColumns(Enum):
    """Enum holding mutable and immutable all_workflow_database.tsv column headers"""


# Immutable class needs to be placed
class ImmutableSubmissionFileHeader(WorkflowDatabaseColumns):
    Date = "DATE"
    Cromwell_Server = "CROMWELL_SERVER"
    Run_ID = "RUN_ID"
    WDL_Name = "WDL_NAME"


class MutableSubmissionFileHeader(WorkflowDatabaseColumns):
    Status = "STATUS"
    Alias = "ALIAS"


def get_submission_file_headers(
    workflow_database_columns=WorkflowDatabaseColumns,
) -> list:
    """
    Retrieves the subclass values from WorkflowDatabaseColumns
    :return: List of submission file headers
    """
    # For loop gets the subclasses in WorkflowDatabaseColumns enum
    # (MutableSubmissionFileHeader and IMMutableSubmissionFileHeader), then another for
    # loop is used to get the values for each subclass. Resulting in a list of lists.
    return sum(  # Sum flattens list of lists in to list
        [
            [key.value for key in sub_cls]
            for sub_cls in workflow_database_columns.__subclasses__()
        ],
        [],
    )
