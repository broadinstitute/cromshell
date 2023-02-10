import shutil
import tempfile
from pathlib import Path

import pytest

from cromshell.submit import command as submit_command


@pytest.fixture
def mock_data_path():
    return Path(__file__).parent.joinpath("mock_data/")


@pytest.fixture
def temp_dir_path():
    return Path(tempfile.gettempdir() + "/test_io_utility/")


class TestSubmit:
    """Test the submit command functions"""

    def test_update_submission_file(self, mock_data_path, tmp_path):
        submission_file_path = mock_data_path.joinpath(
            "submit/submission_file_template.text"
        )
        temp_submission_file = str(tmp_path) + "/submission_file.text"

        # Copy submission file template to temp dir
        shutil.copyfile(submission_file_path, temp_submission_file)

        # Run update submission file command which should append a line to the
        # temp submission with the provided info
        submit_command.add_submission_to_all_database_tsv(
            cromwell_server="https://cromwell-UnitTest.dsde-methods.broadinstitute.org",
            submissions_file=temp_submission_file,
            wdl="/made/up/path/UnitTest.wdl",
            workflow_status={
                "id": "73650b78-64e5-4ce7-a73e-3eb264133f20",
                "status": "Submitted",
            },
        )

        # Create a dic which will be used to test whether the submission
        # correctly added to the submission file
        testing_submission_row = [
            "date_time",
            "https://cromwell-UnitTest.dsde-methods.broadinstitute.org",
            "73650b78-64e5-4ce7-a73e-3eb264133f20",
            "UnitTest.wdl",
            "Submitted",
            "",
        ]

        # Open the temp submission file that was recently updated and compare the last
        # row with the expected
        with open(temp_submission_file) as f:
            last_line = f.readlines()[-1]
            last_line_columns = last_line.split()

            # Compare each column in the last line dictionary with expected
            # results dictionary. Range starts from 1 to skip the date_time column
            # which would be difficult to coordinate a comparison.
            for i in range(1, len(last_line_columns)):
                assert last_line_columns[i] == testing_submission_row[i]
