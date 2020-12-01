import pytest
from cromshell.status import command
from cromshell.utilities import cromshellconfig


class TestStatus:
    """Test the status command"""

    def test_get_metadata_status_summary(self):
        cromshell_config = cromshellconfig
        status = command
        workflow_id = "f373342d-fcfd-4e97-8f6b-cde1ff6ba3ce"
        # status.main(cromshell_config, workflow_id)
        # return_value = status.main.ret_val
        print(cromshell_config.metadata_parameters)

        # assert cromshell_config.metadata_parameters == 1, "Return value should be 1"

    def test_trivial(self):

        x = 1
        y = 1

        assert x == y

    @pytest.mark.parametrize("value", ["atgcX", "L:", "3", "AUGC~", ":gagagag"])
    def test_trivial_with_parameters(self, value):

        with pytest.raises(AssertionError):
            assert value == 1
