import pytest

from cromshell.utilities import io_utils
from pathlib import Path


class TestIOUtilities:
    """Test io_utils  functions and variables"""

    def test_assert_required_file_is_not_empty(self,mock_data_path):

        current_file_name = Path(__file__).parent.absolute()

        # asserts that an exception is raised by the function
        try:
            io_utils.assert_required_file_is_not_empty(
                file_name=current_file_name, file_description="Io utiles"
            )
        except Exception as exc:
            assert False, f"Function should not have raised any exception {exc}"

    @pytest.fixture
    def mock_data_path(self):
        return Path(__file__).parent.joinpath("mock_data/")
