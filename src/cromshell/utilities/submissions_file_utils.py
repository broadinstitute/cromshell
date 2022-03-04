from enum import Enum


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
