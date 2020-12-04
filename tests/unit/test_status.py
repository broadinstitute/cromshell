import pytest
from cromshell.status import command
import os


class TestStatus:
    """Test the status command functions"""

    def get_metadata_status_summary(self, workflow_metadata):
        status_command = command


    @pytest.fixture
    def mock_data_path(self):
        return os.path.join(os.path.dirname(__file__), "mock_data/")
