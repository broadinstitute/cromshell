import csv
import io
import os
import shutil
from contextlib import redirect_stdout
from pathlib import Path

import pytest

from cromshell.utilities import cromshellconfig, io_utils


class TestIOUtilities:
    """Test io_utils  functions and variables"""

    def test_assert_file_is_not_empty_file_exists(self):
        # asserts that an exception is NOT raised by the function,
        # because we are giving the path to this current unit test
        # file which should exist and is not empty.
        current_file_name = Path(__file__).parent.absolute()

        io_utils.assert_file_is_not_empty(
            file_path=current_file_name, file_description="Io Utils"
        )

        # asserts that an exception is raised by the function,
        # because we are giving it a fake file path which shouldn't exist
        with pytest.raises(FileExistsError):
            io_utils.assert_file_is_not_empty(
                file_path="/fake/file/path", file_description="Io Utils"
            ), "Provided a fake file path, function is fail"

    def test_assert_file_is_not_empty(self, tmp_path):
        # Create temp file path
        empty_temp_file_path = tmp_path / "empty.text"
        # Check temp does not exits
        if not os.path.exists(empty_temp_file_path):
            with open(empty_temp_file_path, "w"):  # Create temp file
                pass

        with pytest.raises(EOFError):
            io_utils.assert_file_is_not_empty(
                file_path=empty_temp_file_path, file_description="Io Utils"
            ), "Provided a fake file path, function is fail"

    @pytest.mark.parametrize(
        "workflow_id, validity, assert_msg",
        [
            (
                "7ef69ca-6l9-44489-8ed-fce2876312c",
                False,
                "Should return false if workflow id is not hexadecimal",
            ),
            (
                "7ez69ca5-6l9h-4449-8ej1-mce28763712c",
                False,
                "Should return false if workflow id is not hexadecimal",
            ),
            (
                "7ef69ca5-0a9a-4449-8ed1-fce28763712c",
                True,
                "Should return True with valid ID",
            ),
        ],
    )
    def test_is_workflow_id_valid(self, workflow_id, validity, assert_msg):
        with pytest.raises(TypeError):
            io_utils.is_workflow_id_valid(
                workflow_id=None
            ), "Should raise an error if empty string is given"

        with pytest.raises(ValueError):
            io_utils.is_workflow_id_valid(
                workflow_id=""
            ), "Should raise an error if empty string is given"

        assert (
            bool(io_utils.is_workflow_id_valid(workflow_id=workflow_id)) is validity
        ), assert_msg

    # TODO: test something with at least 1 level of nesting
    #  to show it works on a non-trivial example.
    @pytest.mark.parametrize(
        "testing_input, test_output",
        [
            (
                (
                    """{"id":"4bf7ca9c-0b39-48fb-9af7-83e3e488f62b","status":"Submitted"}"""
                ),
                (
                    """\"{\\"id\\":\\"4bf7ca9c-0b39-48fb-9af7-83e3e488f62b\\",\\"status\\":\\"Submitted\\"}\"\n"""
                ),
            ),
        ],
    )
    def test_pretty_print_json(self, testing_input, test_output):

        # Here the function is being run and allows us to redirect the stdout which
        # would be what the function prints to the screen to file like object
        func_stdout = io.StringIO()
        with redirect_stdout(func_stdout):
            io_utils.pretty_print_json(testing_input)

        # assert the function stdout is the same as the expected out
        assert func_stdout.getvalue() == test_output

    def test_create_directory(self, tmp_path):
        test_io_utility_temp_folder = tmp_path / "test_io_utility"

        # Test that function is able to create a folder.
        io_utils.create_directory(
            dir_path=test_io_utility_temp_folder, parents=False, exist_ok=False
        )
        assert (
            test_io_utility_temp_folder.exists()
        ), "Temp folder should have been created"

    def test_create_directory_exist_ok(self, tmp_path):
        # Create test_io_utility_temp_folder
        test_io_utility_temp_folder = tmp_path / "test_io_utility"
        test_io_utility_temp_folder.mkdir()

        # Test that function fails and raises an error because `exist_ok`
        # is set to `False` and the folder its being asked to create already
        # exists from the previous lines.
        with pytest.raises(FileExistsError):
            io_utils.create_directory(
                dir_path=test_io_utility_temp_folder, parents=False, exist_ok=False
            ), "Should fail because folder already exists from previous test"

        # Test that exception is not raised in this case even though
        # folder already exists, because `exist_ok` variable is set to `True`.
        io_utils.create_directory(
            dir_path=test_io_utility_temp_folder, parents=False, exist_ok=True
        )

    def test_create_directory_parents(self, tmp_path):
        test_io_utility_temp_folder_parents = (
            tmp_path / "test_io_utility" / "parent1" / "parent2"
        )

        # Test that nested folders are not created if `parents` is set to `False`
        with pytest.raises(FileNotFoundError):
            io_utils.create_directory(
                dir_path=test_io_utility_temp_folder_parents,
                parents=False,
                exist_ok=False,
            ), "Should fail because folder is nested and `parents` is set to `False`"

        # Test that nested folders are created if `parents` is set to `True`
        io_utils.create_directory(
            dir_path=test_io_utility_temp_folder_parents, parents=True, exist_ok=False
        )
        assert (
            test_io_utility_temp_folder_parents.exists()
        ), "Temp folder should have been created"

    def test_copy_files_to_directory(self, tmp_path):
        # Test that dummy file should fail
        with pytest.raises(FileNotFoundError):
            io_utils.copy_files_to_directory(
                directory=tmp_path, input_files="/dummy/file"
            ), "Should fail because folder does not exist"

        # Test that dummy dir should fail
        file_to_cp = Path(__file__).absolute()
        with pytest.raises(FileNotFoundError):
            io_utils.copy_files_to_directory(
                directory="/dummy/file/", input_files=file_to_cp
            ), "Should fail because folder does not exist"

        # Test function works with proper dir and file
        io_utils.copy_files_to_directory(directory=tmp_path, input_files=file_to_cp)
        copied_file = Path(tmp_path).joinpath(file_to_cp.name)
        print(copied_file)
        assert copied_file.exists(), "Temp folder should have been created"

        # 'tmp_path' is a default pytest fixture

    @pytest.mark.parametrize(
        "workflow_id, column_to_update, update_value, should_fail",
        [
            [
                "b3b197b3-fdca-4647-9fd8-bf16d2cb734d",
                cromshellconfig.MutableSubmissionFileHeader.Alias.value,
                "wonderwoman",
                False,
            ],
            [
                "b3b197b3-fdca-4647-9fd8-bf16d2cb734d",
                cromshellconfig.MutableSubmissionFileHeader.Status.value,
                "Failed",
                False,
            ],
            [
                "682f3e72-0285-40ec-8128-1feb877706ce",
                cromshellconfig.ImmutableSubmissionFileHeader.WDL_Name.value,
                "Calm.wdl",
                True,
            ],
            [
                "682f3e72-0285-40ec-8128-1feb877706ce",
                cromshellconfig.ImmutableSubmissionFileHeader.Date.value,
                "10date20",
                True,
            ],
            [
                "682f3e72-0285-40ec-8128-1feb877706ce",
                cromshellconfig.ImmutableSubmissionFileHeader.Cromwell_Server.value,
                "testserver",
                True,
            ],
            [
                "682f3e72-0285-40ec-8128-1feb877706ce",
                cromshellconfig.ImmutableSubmissionFileHeader.Run_ID.value,
                "testid",
                True,
            ],
            ["b3b197b3-fdca-4647-9fd8-bf16d2cb734d", "FakeColumn", "wonderwoman", True],
        ],
    )
    def test_update_all_workflow_database_tsv(
        self,
        workflow_id: str,
        column_to_update: str,
        update_value: str,
        submission_file: str,
        should_fail: bool,
        tmp_path,
    ) -> None:

        temp_submission_file = str(tmp_path) + "/submission_file.text"

        # Copy submission file template to temp dir
        shutil.copyfile(submission_file, temp_submission_file)

        if should_fail:
            with pytest.raises(ValueError):
                io_utils.update_all_workflow_database_tsv(
                    workflow_database_path=temp_submission_file,
                    workflow_id=workflow_id,
                    column_to_update=column_to_update,
                    update_value=update_value,
                )
        else:
            # Run function to change alias using the temp submission file
            io_utils.update_all_workflow_database_tsv(
                workflow_database_path=temp_submission_file,
                workflow_id=workflow_id,
                column_to_update=column_to_update,
                update_value=update_value,
            )

            # Open the temp submission file that was recently updated and compare the
            # alias name of the workflow id
            with open(temp_submission_file, "r") as csv_file:
                reader = csv.DictReader(csv_file, delimiter="\t")
                for row in reader:
                    if (
                        row[cromshellconfig.ImmutableSubmissionFileHeader.Run_ID.value]
                        == workflow_id
                    ):
                        assert row[column_to_update] == update_value

    @pytest.fixture
    def mock_data_path(self):
        return Path(__file__).parent.joinpath("mock_data/")

    @pytest.fixture
    def submission_file(self, mock_data_path):
        return mock_data_path.joinpath("all.workflow.database.tsv")
