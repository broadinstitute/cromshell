import pytest

from cromshell.utilities import io_utils
from pathlib import Path, PurePath

import tempfile
import shutil


class TestIOUtilities:
    """Test io_utils  functions and variables"""

    def test_assert_file_is_not_empty(self):

        # asserts that an exception is NOT raised by the function,
        # if file path was not given. In cases an optional file
        # is being checked and the user didn't not provide the file path then no
        # exception should be raised.
        try:
            io_utils.assert_file_is_not_empty(
                file_name=None, file_description="Io Utils"
            )
        except Exception as exc:
            assert False, f"Function should not have raised any exception {exc}"

        # asserts that an exception is NOT raised by the function,
        # because we are giving the path to this current unit test
        # file which should exist.
        current_file_name = Path(__file__).parent.absolute()
        try:
            io_utils.assert_file_is_not_empty(
                file_name=current_file_name, file_description="Io Utils"
            )
        except Exception as exc:
            assert False, f"Function should not have raised any exception {exc}"

        # asserts that an exception is raised by the function,
        # because we are giving the a fake file path which shouldn't exist
        with pytest.raises(Exception):
            io_utils.assert_file_is_not_empty(
                file_name="/fake/file/path", file_description="Io Utils"
            ), "Provided a fake file path, function is fail"

    def test_is_workflow_id_valid(self):

        with pytest.raises(Exception):
            io_utils.is_workflow_id_valid(workflow_id=None), \
            "Should raise an error if empty string is given"

        assert not io_utils.is_workflow_id_valid(
            workflow_id="7ef69ca-6l9-44489-8ed-fce2876312c"), \
            "Workflow ids not following 8-4-4-4-12 bock length " \
            "pattern should return False"

        assert not io_utils.is_workflow_id_valid(
            workflow_id="7ez69ca5-6l9h-4449-8ej1-mce28763712c"), \
            "Workflow ids characters must only be `a` through `f`"

        assert io_utils.is_workflow_id_valid(
            workflow_id="7ef69ca5-0a9a-4449-8ed1-fce28763712c"), \
            "Should return True with valid ID"

    # Skipping because there isn't logic in function. Testing would
    # be helpful later if the function ends up supporting file paths to
    # JSONs or dictionaries as input
    # def test_pretty_print_json(self):

    def test_create_directory(self, temp_dir_path):

        temp_folder = Path(temp_dir_path + "/test_io_utility/")
        temp_folder_parents = Path(temp_dir_path + "/test_io_utility/parent1/parent2/")

        # Delete test dir if exists from previous test run
        if temp_folder.exists():
            shutil.rmtree(temp_folder)

        # Test that function is able to create a folder.
        io_utils.create_directory(dir_path=temp_folder, parents=False, exist_ok=False)
        assert temp_folder.exists(), "Temp folder should have been created"

        # Test that function fails and raises an error because `exist_ok`
        # is set to `False` and the folder its being asked to create already
        # exists from the previous lines.
        with pytest.raises(FileExistsError):
            io_utils.create_directory(
                dir_path=temp_folder, parents=False, exist_ok=False
            ), "Should fail because folder already exists from previous test"

        # Test that exception is not raised in this case even though
        # folder already exists, because `exist_ok` variable is set to `True`.
        try:
            io_utils.create_directory(
                dir_path=temp_folder, parents=False, exist_ok=True
            )
        except Exception as exc:
            assert False, f"Should not raise exception b/c exist_Ok set to True {exc}"

        # Test that nested folders are not created if `parents` is set to `False`
        with pytest.raises(FileNotFoundError):
            io_utils.create_directory(
                dir_path=temp_folder_parents, parents=False, exist_ok=False
            ), "Should fail because folder is nested and `parents` is set to `False`"

        # Test that nested folders are created if `parents` is set to `True`
        io_utils.create_directory(
            dir_path=temp_folder_parents, parents=True, exist_ok=False
        )
        assert temp_folder_parents.exists(), "Temp folder should have been created"

        # Delete temp folder
        shutil.rmtree(temp_folder)

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
        io_utils.copy_files_to_directory(
            directory=temp_folder, input_files=file_to_cp
        )
        copied_file = Path(temp_folder).joinpath(file_to_cp.name)
        print(copied_file)
        assert copied_file.exists(), "Temp folder should have been created"
        # Delete temp folder
        shutil.rmtree(temp_folder)

    #def test_log_error_and_raise_exception(self):

    @pytest.fixture
    def mock_data_path(self):
        return Path(__file__).parent.joinpath("mock_data/")

    @pytest.fixture
    def temp_dir_path(self):
        return tempfile.gettempdir()
