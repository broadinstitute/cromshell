import shutil
import tempfile
from pathlib import Path

import pytest

from cromshell.submit import command as submit_command


@pytest.fixture
def mock_data_path():
    return Path(__file__).parent.joinpath("mock_data/")


workflows_path = Path(__file__).parents[1].joinpath("workflows/")


@pytest.fixture
def temp_dir_path():
    return Path(tempfile.gettempdir() + "/test_io_utility/")


class TestSubmit:
    """Test the submit command functions"""

    womtool_path = shutil.which("womtool")
    if womtool_path is not None:  # If womtool is installed run womtool validation tests

        @pytest.mark.parametrize(
            "test_wdl_path, test_json_path",
            [
                (
                    workflows_path.joinpath("not_valid.wdl"),
                    workflows_path.joinpath("helloWorld.json"),
                ),
                (
                    workflows_path.joinpath("helloWorld.wdl"),
                    workflows_path.joinpath("not_valid.json"),
                ),
                (
                    workflows_path.joinpath("not_valid.wdl"),
                    workflows_path.joinpath("not_valid.json"),
                ),
            ],
        )
        def test_womtool_validate_not_valid_wdl_and_json(
            self, test_wdl_path, test_json_path
        ):

            # asserts that an exception is raised by the function
            with pytest.raises(submit_command.ValidationError):
                submit_command.womtool_validate_wdl_and_json(
                    wdl=str(test_wdl_path), wdl_json=str(test_json_path)
                ), "Womtool should have marked not valid workflow as not valid."

        def test_womtool_validate_valid_wdl_and_json(self):
            workflow_wdl_path = workflows_path.joinpath("helloWorld.wdl")
            workflow_json_path = workflows_path.joinpath("helloWorld.json")

            assert (
                submit_command.womtool_validate_wdl_and_json(
                    wdl=str(workflow_wdl_path), wdl_json=str(workflow_json_path)
                )
                == 0
            ), "Womtool should have marked valid workflow as valid."

    def test_update_submission_file(self, mock_data_path, tmp_path):

        submission_file_path = mock_data_path.joinpath(
            "submit/submission_file_template.text"
        )
        temp_submission_file = str(tmp_path) + "/submission_file.text"

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
