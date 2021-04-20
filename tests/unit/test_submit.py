import os
import shutil
import tempfile
from pathlib import Path

import pytest

from cromshell.submit import command as submit_command


class TestSubmit:
    """Test the submit command functions"""

    # Skipping test because function simply holds other functions
    # def test_validate_input(self, mock_data_path):

    def test_womtool_validate_invalid_wdl_and_json(self, workflows_path):
        workflow_wdl_path = workflows_path.joinpath("not_valid.wdl")
        workflow_json_path = workflows_path.joinpath("not_valid.json")

        # asserts that an exception is raised by the function
        with pytest.raises(Exception):
            submit_command.womtool_validate_wdl_and_json(
                wdl=workflow_wdl_path, wdl_json=workflow_json_path
            )

    def test_womtool_validate_valid_wdl_and_json(self, workflows_path):
        workflow_wdl_path = workflows_path.joinpath("helloWorld.wdl")
        workflow_json_path = workflows_path.joinpath("helloWorld.json")

        assert (
            submit_command.womtool_validate_wdl_and_json(
                wdl=workflow_wdl_path, wdl_json=workflow_json_path
            )
            == 0
        ), "Womtool should have marked valid workflow as valid."

    # Skipping test because function requires connection to cromwell server
    # def test_submit_workflow_to_server(self, mock_data_path):

    def test_update_submission_file(self, mock_data_path, temp_dir_path):

        submission_file_path = mock_data_path.joinpath(
            "submit/submission_file_template.text"
        )
        temp_submission_file = str(temp_dir_path) + "/submission_file.text"
        # Create a temp dir to store temp submission file
        os.mkdir(temp_dir_path)
        # Copy submission file template to temp dir
        shutil.copyfile(submission_file_path, temp_submission_file)

        # Run update submission file command which should append a line to the
        # temp submission with the provided info
        submit_command.update_submission_file(
            cromwell_server="https://cromwell-UnitTest.dsde-methods.broadinstitute.org",
            submission_file=temp_submission_file,
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

        # Delete temp dir with template
        shutil.rmtree(temp_dir_path)

    @pytest.fixture
    def mock_data_path(self):
        return Path(__file__).parent.joinpath("mock_data/")

    @pytest.fixture
    def workflows_path(self):
        return Path(__file__).parents[1].joinpath("workflows/")

    @pytest.fixture
    def temp_dir_path(self):
        return Path(tempfile.gettempdir() + "/test_io_utility/")
