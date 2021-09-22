import os

import pytest
from click.testing import CliRunner
import json

from cromshell.__main__ import main_entry as cromshell
from traceback import print_exception
from pathlib import Path


class TestSubmit:
    @pytest.mark.parametrize(
        "wdl, json_file, exit_code",
        [
            ("tests/workflows/helloWorld.wdl", "tests/workflows/helloWorld.json", 0),
            ("tests/workflows/helloWorld.wdl", "tests/workflows/not_valid.json", 1),
            ("tests/workflows/not_valid.wdl", "tests/workflows/helloWorld.json", 1),
        ],
    )
    def test_submit(
            self, local_cromwell_url: str, wdl: str, json_file: str, exit_code: int
    ):
        runner = CliRunner(mix_stderr=False)
        # The absolute path will be passed to the invoke command because
        # the test is being run in temp directory created by CliRunner.
        absolute_wdl = str(Path(wdl).resolve())
        absolute_json = str(Path(json_file).resolve())
        with runner.isolated_filesystem():
            result = runner.invoke(
                cromshell,
                [
                    "--cromwell_url",
                    local_cromwell_url,
                    "submit",
                    absolute_wdl,
                    absolute_json,
                ],
            )
            assert result.exit_code == exit_code, (
                f"\nSTDOUT:\n{result.stdout}"
                f"\nSTDERR:\n{result.stderr}"
                f"\nExceptions:\n{result.exception}"
                f"\n{print_exception(*result.exc_info)}"
            )

            # Check if workflow id added to local database file
            # if exit_code == 0:
            #     stdout_dict = json.loads(str(result.stdout).strip())
            #     assert stdout_dict == "lawl"

    def test_submit_cromshell_folders_created(
            self, local_server_folder, local_hidden_cromshell_folder
    ):
        # Created hidden cromshell directory
        assert Path.exists(local_hidden_cromshell_folder)
        # Created a directory to hold function input files, using server name
        assert Path.exists(local_server_folder)


    @pytest.fixture
    def local_cromwell_url(self):
        return "http://localhost:8000"

    @pytest.fixture
    def local_hidden_cromshell_folder(self):
        return Path(os.environ.get("TMPDIR")).joinpath(".cromshell")

    @pytest.fixture
    def local_server_folder(self, local_hidden_cromshell_folder, local_cromwell_url):
        stripped_cromwell_url = local_cromwell_url.replace("http://", "")
        return Path(local_hidden_cromshell_folder).joinpath(stripped_cromwell_url)
