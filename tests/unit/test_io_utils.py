import io
import os
import shutil
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

import pytest

from cromshell.utilities import io_utils


class TestIOUtilities:
    """Test io_utils  functions and variables"""

    def test_assert_file_is_not_empty_file_exists(self):

        # asserts that an exception is NOT raised by the function,
        # because we are giving the path to this current unit test
        # file which should exist and is not empty.
        current_file_name = Path(__file__).parent.absolute()
        try:
            io_utils.assert_file_is_not_empty(
                file_path=current_file_name, file_description="Io Utils"
            )
        except Exception as exc:
            assert False, f"Function should not have raised any exception {exc}"

        # asserts that an exception is raised by the function,
        # because we are giving it a fake file path which shouldn't exist
        with pytest.raises(FileExistsError):
            io_utils.assert_file_is_not_empty(
                file_path="/fake/file/path", file_description="Io Utils"
            ), "Provided a fake file path, function is fail"

    def test_assert_file_is_not_empty(self, temp_dir_path):

        # Create temp file path
        empty_temp_file_path = Path(temp_dir_path + "/empty.text")
        # Check temp does not exits
        if not os.path.exists(empty_temp_file_path):
            with open(empty_temp_file_path, "w"):  # Create temp file
                pass

        with pytest.raises(EOFError):
            io_utils.assert_file_is_not_empty(
                file_path=empty_temp_file_path, file_description="Io Utils"
            ), "Provided a fake file path, function is fail"

        # Delete temp file
        os.remove(empty_temp_file_path)

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

    def test_pretty_print_json(self):

        # String holds the expected printout from function in a string, which includes
        # 4 space indentation and new line characters
        testing_out = (
            """{\n    "id": "4bf7ca9c-0b39-48fb-9af7-83e3e488f62b",\n"""
            """    "status": "Submitted"\n}\n"""
        )

        # Here the function is being run and allows us to redirect the stdout which
        # would be what the function prints to the screen to file like object
        func_stdout = io.StringIO()
        with redirect_stdout(func_stdout):
            io_utils.pretty_print_json(
                """{"id": "4bf7ca9c-0b39-48fb-9af7-83e3e488f62b",
                "status": "Submitted"}"""
            )

        # assert the function stdout is the same as the expected out
        assert func_stdout.getvalue() == testing_out

    def test_create_directory(self, temp_dir_path):

        test_io_utility_temp_folder = Path(temp_dir_path + "/test_io_utility/")

        # Delete test dir if exists from previous test run
        if test_io_utility_temp_folder.exists():
            shutil.rmtree(test_io_utility_temp_folder)

        # Test that function is able to create a folder.
        io_utils.create_directory(
            dir_path=test_io_utility_temp_folder, parents=False, exist_ok=False
        )
        assert (
            test_io_utility_temp_folder.exists()
        ), "Temp folder should have been created"

        # Delete temp folder
        shutil.rmtree(test_io_utility_temp_folder)

    def test_create_directory_exist_ok(self, temp_dir_path):
        test_io_utility_temp_folder = Path(temp_dir_path + "/test_io_utility/")

        # Delete test dir if exists from previous test run
        if test_io_utility_temp_folder.exists():
            shutil.rmtree(test_io_utility_temp_folder)

        # Create test_io_utility_temp_folder
        os.mkdir(test_io_utility_temp_folder)

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

        # Delete temp folder
        shutil.rmtree(test_io_utility_temp_folder)

    def test_create_directory_parents(self, temp_dir_path):

        test_io_utility_temp_folder = Path(temp_dir_path + "/test_io_utility/")
        test_io_utility_temp_folder_parents = Path(
            temp_dir_path + "/test_io_utility/parent1/parent2/"
        )

        # Delete test dir if exists from previous test run
        if test_io_utility_temp_folder.exists():
            shutil.rmtree(test_io_utility_temp_folder)

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

        # Delete temp folder
        shutil.rmtree(test_io_utility_temp_folder)

    def test_copy_files_to_directory(self, temp_dir_path):

        temp_folder = Path(temp_dir_path + "/test_io_utility/")
        io_utils.create_directory(temp_folder)

        # Test that dummy file should fail
        with pytest.raises(FileNotFoundError):
            io_utils.copy_files_to_directory(
                directory=temp_folder, input_files="/dummy/file"
            ), "Should fail because folder does not exist"

        # Test that dummy dir should fail
        file_to_cp = Path(__file__).absolute()
        with pytest.raises(FileNotFoundError):
            io_utils.copy_files_to_directory(
                directory="/dummy/file/", input_files=file_to_cp
            ), "Should fail because folder does not exist"

        # Test function works with proper dir and file
        io_utils.copy_files_to_directory(directory=temp_folder, input_files=file_to_cp)
        copied_file = Path(temp_folder).joinpath(file_to_cp.name)
        print(copied_file)
        assert copied_file.exists(), "Temp folder should have been created"
        # Delete temp folder
        shutil.rmtree(temp_folder)

    @pytest.fixture
    def mock_data_path(self):
        return Path(__file__).parent.joinpath("mock_data/")

    @pytest.fixture
    def temp_dir_path(self):
        return tempfile.gettempdir()
