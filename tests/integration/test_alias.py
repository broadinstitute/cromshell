import csv
import os
import shutil
from pathlib import Path
from traceback import print_exception

import pytest
from click.testing import CliRunner

from cromshell.__main__ import main_entry as cromshell


def run_cromshell_alias(workflow_id: str, alias_name: str, exit_code: int):
    """Run cromshell alias using CliRunner and assert job is successful"""

    runner = CliRunner(mix_stderr=False)
    # The absolute path will be passed to the invoke command because
    # the test is being run in temp directory created by CliRunner.
    with runner.isolated_filesystem():
        result = runner.invoke(
            cromshell,
            [
                "alias",
                workflow_id,
                alias_name,
            ],
        )
        assert result.exit_code == exit_code, (
            f"\nSTDOUT:\n{result.stdout}"
            f"\nSTDERR:\n{result.stderr}"
            f"\nExceptions:\n{result.exception}"
            f"\n{print_exception(*result.exc_info)}"
        )
        return result


def assert_workflow_id_matches_alias(
    workflow_id: str, alias_name: str, local_workflow_database_tsv: str
):
    """
    For a given workflow id assert that the alias matches a given alias name
    """
    with open(local_workflow_database_tsv, "r") as csv_file:
        reader = csv.DictReader(csv_file, delimiter="\t")
        for row in reader:
            if row["RUN_ID"] == workflow_id:
                #  If alias_name is "" (which is when we want to remove an alias) assert
                #  that the alias for the workflow id returns None. Else (when adding
                #  and alias) assert that the alias for the workflow id returns
                #  the matching alias name.
                if alias_name == "":
                    assert row["ALIAS"] is None
                else:
                    assert row["ALIAS"] == alias_name


class TestAlias:
    @pytest.mark.parametrize(
        "workflow_id, alias_name, exit_code",
        [
            ("b3b197b3-fdca-4647-9fd8-bf16d2cb734d", "breath", 0),
            ("a63aa10c-a43e-4ca7-9be9-c2d2aa08b96d", "", 0),
            (
                "682f3e72-0285-40ec-8128-1feb877706ce",
                "wombat",
                1,  # Should fail because alias already being used
            ),
        ],
    )
    def test_alias(
        self,
        local_cromwell_url: str,
        local_workflow_database_tsv: str,
        mock_workflow_database_tsv: str,
        workflow_id: str,
        alias_name: str,
        exit_code: int,
    ):
        # Copy template all.workflow.database.tsv to cromshell hidden folder
        shutil.copyfile(mock_workflow_database_tsv, local_workflow_database_tsv)

        # Run cromshell alias
        run_cromshell_alias(
            workflow_id=workflow_id,
            alias_name=alias_name,
            exit_code=exit_code,
        )

        # If command passed, check the alias of the workflow id in database tsv
        if exit_code == 0:
            assert_workflow_id_matches_alias(
                workflow_id=workflow_id,
                alias_name=alias_name,
                local_workflow_database_tsv=local_workflow_database_tsv,
            )

    @pytest.fixture
    def local_cromwell_url(self):
        return "http://localhost:8000"

    @pytest.fixture  # Env variable set in tox.ini
    def local_hidden_cromshell_folder(self):
        return Path(os.environ.get("CROMSHELL_CONFIG")).joinpath(".cromshell")

    @pytest.fixture
    def local_workflow_database_tsv(self, local_hidden_cromshell_folder):
        return Path(local_hidden_cromshell_folder).joinpath("all.workflow.database.tsv")

    @pytest.fixture
    def mock_data_path(self):
        return Path(__file__).parent.joinpath("mock_data/")

    @pytest.fixture
    def mock_workflow_database_tsv(self, mock_data_path):
        return mock_data_path.joinpath("all.workflow.database.tsv")
