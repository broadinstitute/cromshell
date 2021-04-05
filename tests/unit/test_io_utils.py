import pytest

from cromshell.utilities import io_utils
from pathlib import Path


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

