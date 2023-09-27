import csv
import io
import os
import re
import shutil
import tempfile
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import NamedTemporaryFile
from zipfile import ZipFile

import pytest

import cromshell.utilities.submissions_file_utils
from cromshell.utilities import io_utils, submissions_file_utils


class TestIOUtilities:
    """Test io_utils  functions and variables"""

    def test_assert_path_is_not_empty_file_exists(self):
        # asserts that an exception is NOT raised by the function,
        # because we are giving the path to this current unit test
        # file which should exist and is not empty.
        current_file_name = Path(__file__).parent.absolute()

        io_utils.assert_path_is_not_empty(
            path=current_file_name, description="Io Utils"
        )

        # asserts that an exception is raised by the function,
        # because we are giving it a fake file path which shouldn't exist
        with pytest.raises(FileExistsError):
            io_utils.assert_path_is_not_empty(
                path="/fake/file/path", description="Io Utils"
            ), "Provided path to an empty file, function expected to fail"

    def test_assert_path_is_not_empty(self, tmp_path):
        # Check for empty directory
        if len(os.listdir(tmp_path)) != 0:
            with pytest.raises(EOFError):
                io.utils.assert_path_is_not_empty(
                    path=tmp_path, description="Io Utils"
                ), "Provided an empty dir, function expected to fail"

        # Create temp file path
        empty_temp_file_path = tmp_path / "empty.text"
        # Check temp does not exits
        if not os.path.exists(empty_temp_file_path):
            with open(empty_temp_file_path, "w"):  # Create temp file
                pass

        with pytest.raises(EOFError):
            io_utils.assert_path_is_not_empty(
                path=empty_temp_file_path, description="Io Utils"
            ), "Provided a fake file path, function expected to fail"

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
        "testing_input, add_color, test_output",
        [
            (
                """{"id":"4bf7ca9c-0b39-48fb-9af7-83e3e488f62b","status":"Submitted"}""",
                False,
                """\"{\\"id\\":\\"4bf7ca9c-0b39-48fb-9af7-83e3e488f62b\\",\\"status\\":\\"Submitted\\"}\"\n""",
            ),
            (
                """{"id":"4bf7ca9c-0b39-48fb-9af7-83e3e488f62b","status":"Submitted"}""",
                True,
                """\x1b[33m"{\\"id\\":\\"4bf7ca9c-0b39-48fb-9af7-83e3e488f62b\\",\\"status\\":\\"Submitted\\"}"\x1b[39;49;00m\x1b[37m\x1b[39;49;00m\n\n""",
            ),
        ],
    )
    def test_pretty_print_json(self, testing_input, add_color, test_output):
        # Here the function is being run and allows us to redirect the stdout which
        # would be what the function prints to the screen to file like object
        func_stdout = io.StringIO()
        with redirect_stdout(func_stdout):
            io_utils.pretty_print_json(testing_input, add_color=add_color)

        print(func_stdout.getvalue())

        # assert the function stdout is the same as the expected out
        assert func_stdout.getvalue() == test_output

    def test_open_or_zip_directory(self, tmp_path: Path) -> None:
        zip_dir = tmp_path / "my_dir"
        sub_dir = zip_dir / "sub_dir"
        file_1 = zip_dir / "1.txt"
        file_2 = zip_dir / "2.txt"
        file_3 = sub_dir / "3.txt"
        zip_dir.mkdir()
        sub_dir.mkdir()
        file_1.touch()
        file_2.touch()
        file_3.touch()
        with io_utils.open_or_zip(zip_dir) as content:
            with ZipFile(content, "r") as zip_obj:
                assert sorted(zip_obj.namelist()) == [
                    "1.txt",
                    "2.txt",
                    "sub_dir/",
                    "sub_dir/3.txt",
                ]

    def test_open_or_zip_file(self, tmp_path: Path) -> None:
        zip_dir = tmp_path / "my_dir"
        existing_zip = zip_dir / "existing.zip"
        zip_dir.mkdir()
        file_contents = "I'm a zip, I swear."
        existing_zip.write_text(file_contents)
        with io_utils.open_or_zip(existing_zip) as content:
            assert content.read().decode() == file_contents

    def test_open_or_zip_none(self) -> None:
        with io_utils.open_or_zip(None) as content:
            assert content is None

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
                directory=tmp_path, inputs="/dummy/file"
            ), "Should fail because folder does not exist"

        # Test that dummy dir should fail
        file_to_cp = Path(__file__).absolute()
        with pytest.raises(FileNotFoundError):
            io_utils.copy_files_to_directory(
                directory="/dummy/file/", inputs=file_to_cp
            ), "Should fail because folder does not exist"

        # Test function works with proper dir and file
        io_utils.copy_files_to_directory(directory=tmp_path, inputs=file_to_cp)
        copied_file = Path(tmp_path).joinpath(file_to_cp.name)
        print(copied_file)
        assert copied_file.exists(), "Temp folder should have been created"

        # Test function works with proper dir and list of file
        io_utils.copy_files_to_directory(directory=tmp_path, inputs=[file_to_cp])
        copied_file = Path(tmp_path).joinpath(file_to_cp.name)
        print(copied_file)
        assert copied_file.exists(), "Temp folder should have been created from a list"

        # Test function works with two proper dirs
        src_dir = Path(tmp_path) / "copy_src"
        src_file = src_dir / "hello.txt"
        dst_dir = Path(tmp_path) / "copy_dst"
        src_dir.mkdir()
        src_file.touch()
        dst_dir.mkdir()
        io_utils.copy_files_to_directory(directory=dst_dir, inputs=src_dir)
        copied_file = dst_dir / src_dir.name / src_file.name
        assert copied_file.exists(), "Temp folder should have been copied"

        # Test function works with None
        io_utils.copy_files_to_directory(directory=tmp_path, inputs=None)

        # 'tmp_path' is a default pytest fixture

    @pytest.mark.parametrize(
        "contains_wdl, expected_exception",
        [
            (True, None),  # Directory contains a WDL file, no exception expected
            (
                False,
                FileNotFoundError,
            ),  # Directory does not contain a WDL file, expect FileNotFoundError
        ],
    )
    def test_check_if_dir_contains_wdl(self, contains_wdl, expected_exception, tmpdir):
        # Create a temporary directory and conditionally add a WDL file
        test_dir = Path(tmpdir) / "test_dir"
        test_dir.mkdir()

        if contains_wdl:
            (test_dir / "test.wdl").touch()

        # Call the function and assert the exception (if any)
        if expected_exception:
            with pytest.raises(expected_exception):
                io_utils.check_if_dir_contains_wdl(test_dir)
        else:
            io_utils.check_if_dir_contains_wdl(test_dir)

    @pytest.mark.parametrize(
        "workflow_id, column_to_update, update_value, should_fail",
        [
            [
                "b3b197b3-fdca-4647-9fd8-bf16d2cb734d",
                submissions_file_utils.MutableSubmissionFileHeader.Alias.value,
                "wonderwoman",
                False,
            ],
            [
                "b3b197b3-fdca-4647-9fd8-bf16d2cb734d",
                submissions_file_utils.MutableSubmissionFileHeader.Status.value,
                "Failed",
                False,
            ],
            [
                "682f3e72-0285-40ec-8128-1feb877706ce",
                submissions_file_utils.ImmutableSubmissionFileHeader.WDL_Name.value,
                "Calm.wdl",
                True,
            ],
            [
                "682f3e72-0285-40ec-8128-1feb877706ce",
                submissions_file_utils.ImmutableSubmissionFileHeader.Date.value,
                "10date20",
                True,
            ],
            [
                "682f3e72-0285-40ec-8128-1feb877706ce",
                submissions_file_utils.ImmutableSubmissionFileHeader.Cromwell_Server.value,
                "testserver",
                True,
            ],
            [
                "682f3e72-0285-40ec-8128-1feb877706ce",
                submissions_file_utils.ImmutableSubmissionFileHeader.Run_ID.value,
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
            with pytest.raises(KeyError):
                cromshell.utilities.submissions_file_utils.update_row_values_in_submission_db(
                    workflow_database_path=temp_submission_file,
                    workflow_id=workflow_id,
                    column_to_update=column_to_update,
                    update_value=update_value,
                )
        else:
            # Run function to change alias using the temp submission file
            cromshell.utilities.submissions_file_utils.update_row_values_in_submission_db(
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
                        row[
                            submissions_file_utils.ImmutableSubmissionFileHeader.Run_ID.value
                        ]
                        == workflow_id
                    ):
                        assert row[column_to_update] == update_value

    @pytest.mark.parametrize(
        "wdl_content, expected_result",
        [
            ('import "other.wdl"', False),  # No nested import
            ('import "../nested/other.wdl"', True),  # Nested import
            ('import "nested/other.wdl"', False),  # Relative path, but not nested
            ("task my_task { command { echo 'Hello, World!' } }", False),  # No import
            (
                'import "../nested/other.wdl"\nimport "nested/another.wdl"',
                True,
            ),  # Multiple imports, one nested
        ],
    )
    def test_has_nested_dependencies(self, wdl_content, expected_result):
        # Create a temporary file with the provided WDL content
        with NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_file.write(wdl_content)

        wdl_path = Path(temp_file.name)

        # Call the function with the temporary file path
        result = io_utils.has_nested_dependencies(wdl_path)

        # Check if the result matches the expected outcome
        assert result == expected_result

        # Clean up the temporary file
        wdl_path.unlink()

    @pytest.mark.parametrize(
        "wdl_path, flattened_wdl_file",
        [
            ("/dir/path/2/wdl.wdl", "dir-path-2-wdl.wdl"),
            ("/another/wdl.wdl", "another-wdl.wdl"),
        ],
    )
    def test_get_flattened_filename(self, wdl_path, flattened_wdl_file):
        # Create a TemporaryDirectory to simulate tempdir
        with tempfile.TemporaryDirectory() as tempdir:
            # tempdir = Path(tempdir_name)
            wdl_path = Path(wdl_path)

            # Call the function with the simulated tempdir and wdl_path
            result = io_utils.get_flattened_filename(tempdir, wdl_path)

            # Check if the result matches the expected outcome
            assert result == Path(tempdir).joinpath(flattened_wdl_file)

    # Define test cases using @pytest.mark.parametrize
    @pytest.mark.parametrize(
        "wdl_path, expected_file_content",
        [
            (
                "wdl_with_imports/helloWorld_with_imports.wdl",
                ["-helloWorld.wdl", "-wdl_with_imports-hello_world_task.wdl"],
            ),
        ],
    )
    def test_flatten_nested_dependencies(
        self, wdl_path, expected_file_content, test_workflows_path
    ):
        # Create a temporary directory to simulate tempdir

        tempdir = tempfile.TemporaryDirectory()
        abs_wdl_path = test_workflows_path.joinpath(wdl_path)

        abs_wdl_path_str = str(abs_wdl_path.absolute())

        # Call the function with the simulated tempdir and wdl_path
        result_path = io_utils.flatten_nested_dependencies(
            tempdir=tempdir, wdl_path=abs_wdl_path_str
        )

        # Check if the result matches the expected outcome
        expected_result_path = Path(tempdir.name).joinpath(
            re.sub("^-", "", re.sub("/", "-", str(abs_wdl_path)))
        )
        assert result_path == expected_result_path

        # Check if the expected file content is in the result file
        for expected_file_content_line in expected_file_content:
            parsed_line = (
                re.sub("^-", "", re.sub("/", "-", str(abs_wdl_path.parents[1])))
                + expected_file_content_line
            )
            assert parsed_line in result_path.read_text()

        # Clean up the temporary directory
        tempdir.cleanup()

    @pytest.fixture
    def mock_data_path(self):
        return Path(__file__).parent.joinpath("mock_data/")

    @pytest.fixture
    def submission_file(self, mock_data_path):
        return mock_data_path.joinpath("all.workflow.database.tsv")
