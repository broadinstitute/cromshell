import json
import os
from pathlib import Path
from traceback import print_exception

import pytest
from click.testing import CliRunner

from cromshell.__main__ import main_entry as cromshell


def run_cromshell_submit(
    wdl: str, json_file: str, local_cromwell_url: str, exit_code: int
):
    """Run cromshell submit using CliRunner and assert job is successful"""

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
                "--hide_logo",
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
        return result


def workflow_id_in_txt_db(result, local_workflow_database_tsv: Path):
    """Get workflow id and assert it is listed in the local workflow database tsv"""

    stdout_substring_formatted = json.loads(result.stdout)
    test_workflow_id = stdout_substring_formatted["id"]

    # check if workflow id is in database tsv
    with open(local_workflow_database_tsv, "r") as file1:

        # read file content
        readfile = file1.read()
        # checking condition for string found or not
        if test_workflow_id in readfile:
            found = True
        else:
            found = False

        assert found, "Workflow ID was not found in /all.workflow.database.tsv"


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
        self,
        local_cromwell_url: str,
        wdl: str,
        json_file: str,
        exit_code: int,
        local_hidden_cromshell_folder: Path,
        local_workflow_database_tsv: Path,
    ):
        # Run cromshell submit
        result = run_cromshell_submit(
            wdl=wdl,
            json_file=json_file,
            exit_code=exit_code,
            local_cromwell_url=local_cromwell_url,
        )

        # If submission passed check workflow id in database tsv
        if exit_code == 0:
            workflow_id_in_txt_db(
                result=result, local_workflow_database_tsv=local_workflow_database_tsv
            )

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
    def local_workflow_database_tsv(self, local_hidden_cromshell_folder):
        return Path(local_hidden_cromshell_folder).joinpath("all.workflow.database.tsv")

    @pytest.fixture
    def local_server_folder(self, local_hidden_cromshell_folder, local_cromwell_url):
        stripped_cromwell_url = local_cromwell_url.replace("http://", "")
        return Path(local_hidden_cromshell_folder).joinpath(stripped_cromwell_url)
