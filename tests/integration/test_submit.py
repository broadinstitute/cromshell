import pytest
from click.testing import CliRunner

from cromshell.__main__ import main_entry as cromshell


class TestSubmit:
    def test_submit(self, local_cromwell_url: str):

        runner = CliRunner()
        result = runner.invoke(cromshell,
                               [
                                   "--cromwell_url",
                                   local_cromwell_url,
                                   "submit",
                                   "tests/workflows/helloWorld.wdl",
                                   "tests/workflows/helloWorld.json",
                               ])
        assert result.exit_code == 0, f"{result.stdout} \n {result.exception}"

    @pytest.fixture
    def local_cromwell_url(self):
        return "http://localhost:8000"
