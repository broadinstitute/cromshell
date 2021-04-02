import shutil
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
            is 0
        ), "Womtool should have marked valid workflow as valid."

    # Skipping test because function requires connection to cromwell server
    # def test_submit_workflow_to_server(self, mock_data_path):

    def test_update_submission_file(self, mock_data_path):
        submission_file_path = mock_data_path.joinpath("submit/submission_file.text")
        submission_file_template_path = mock_data_path.joinpath(
            "submit/submission_file_template.text"
        )

        submit_command.update_submission_file(
            cromwell_server="https://cromwell-UnitTest.dsde-methods.broadinstitute.org",
            submission_file=submission_file_path,
            wdl="/made/up/path/UnitTest.wdl",
            workflow_status={
                "id": "73650b78-64e5-4ce7-a73e-3eb264133f20",
                "status": "Submitted",
            },
        )

        testing_submission_row = [
            "date_time",
            "https://cromwell-UnitTest.dsde-methods.broadinstitute.org",
            "73650b78-64e5-4ce7-a73e-3eb264133f20",
            "UnitTest.wdl",
            "Submitted",
            "",
        ]
        # Open the mock submission file that was recently updated and compare the last
        # row with the expected
        with open(submission_file_path) as f:
            last_line = f.readlines()[-1]
            last_line_columns = last_line.split("\t")

            assert last_line_columns[1] == testing_submission_row[1]
            assert last_line_columns[2] == testing_submission_row[2]
            assert last_line_columns[3] == testing_submission_row[3]
            assert last_line_columns[4] == testing_submission_row[4]
            assert last_line_columns[4] == testing_submission_row[4]

        # Reset mock submission file with template
        shutil.copy(submission_file_template_path, submission_file_path)

    @pytest.fixture
    def mock_data_path(self):
        return Path(__file__).parent.joinpath("mock_data/")

    @pytest.fixture
    def workflows_path(self):
        return Path(__file__).parents[1].joinpath("workflows/")
