import os

from cromshell.utilities import submissions_file_utils as sfu


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
