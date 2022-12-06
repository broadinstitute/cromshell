import os

from cromshell.utilities import submissions_file_utils as sfu
from cromshell.utilities.submissions_file_utils import update_submission_db_format


class TestSubmissionsFileUtils:
    """Test the submission_file_utils config functions and variables"""

    def test_get_submission_file_headers(self, mock_data_path):
        all_workflow_database_tsv = os.path.join(
            mock_data_path, "all.workflow.database.tsv"
        )

        with open(all_workflow_database_tsv, "r") as f:
            first_line = f.readline().strip()

        all_headers = first_line.split("\t")

        assert sfu.WorkflowDatabaseColumns.get_submission_file_headers() == all_headers

    def test_ensure_correct_submission_database_format__correct_database(self, tmpdir):
        """When the database is fine, ensure it is not touched"""

        database_path = tmpdir.join("tmp.database.tsv")
        with open(database_path, "w") as f:
            f.write(
                "DATE\tCROMWELL_SERVER\tRUN_ID\tWDL_NAME\tSTATUS\tALIAS\ndate\tserver\trun\twdl\tstatus\talias"
            )

        old_format = update_submission_db_format(
            submission_file_path=database_path,
        )
        assert (
            not old_format
        ), "cromshellconfig.__ensure_correct_submission_database_format thought a correct database was incorrect"

    def test_ensure_correct_submission_database_format__old_database(self, tmpdir):
        """When the database is fine, ensure it is not touched"""

        database_path = tmpdir.join("tmp.database.tsv")
        with open(database_path, "w") as f:
            f.write(
                "DATE CROMWELL_SERVER RUN_ID WDL_NAME STATUS ALIAS\ndate server run wdl status alias"
            )

        # ensure that the function identifies the old database format and attempts a fix
        old_format = update_submission_db_format(
            submission_file_path=database_path,
        )
        assert (
            old_format
        ), "cromshellconfig.__ensure_correct_submission_database_format failed to identify an incorrect database"

        # see if it's actually fixed
        old_format = update_submission_db_format(
            submission_file_path=database_path,
        )
        assert (
            not old_format
        ), "An old database was not fixed by cromshellconfig.__ensure_correct_submission_database_format"
