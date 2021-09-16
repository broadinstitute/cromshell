import pytest
from click.testing import CliRunner

from cromshell.__main__ import main_entry as cromshell
from traceback import print_exception


class TestSubmit:
    @pytest.mark.parametrize(
        "wdl, json, exit_code",
        [
            ("tests/workflows/helloWorld.wdl", "tests/workflows/helloWorld.json", 0),
            ("tests/workflows/helloWorld.wdl", "tests/workflows/not_valid.json", 1),
            ("tests/workflows/not_valid.wdl", "tests/workflows/helloWorld.json", 1),
        ],
    )
    def test_submit(self, local_cromwell_url: str, wdl: str, json: str, exit_code: int):
        runner = CliRunner(mix_stderr=False)
        result = runner.invoke(
            cromshell,
            [
                "--cromwell_url",
                local_cromwell_url,
                "submit",
                wdl,
                json,
            ],
        )
        assert result.exit_code == exit_code, (
            f"\nSTDOUT:\n{result.stdout}"
            f"\nSTDERR:\n{result.stderr}"
            f"\nExceptions:\n{result.exception}"
            f"\n{print_exception(*result.exc_info)}"
        )

        # Create a directory to hold function input files, using server name
        # Copy input to run directory
        # Update config.submission_file_path:

    @pytest.fixture
    def local_cromwell_url(self):
        return "http://localhost:8000"
