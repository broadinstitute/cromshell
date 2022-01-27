import csv
import shutil
from traceback import print_exception

import pytest
from click.testing import CliRunner
import hashlib

from cromshell.__main__ import main_entry as cromshell
from cromshell.utilities.cromshellconfig import AllWorkflowDatabaseColumns


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
                "--",
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
            if row[AllWorkflowDatabaseColumns.Run_ID.value] == workflow_id:
                #  If alias_name is "" (which is when we want to remove an alias) assert
                #  that the alias for the workflow id returns None. Else (when adding
                #  and alias) assert that the alias for the workflow id returns
                #  the matching alias name.
                if alias_name == "":
                    assert row[AllWorkflowDatabaseColumns.Alias.value] is None
                else:
                    assert row[AllWorkflowDatabaseColumns.Alias.value] == alias_name


class TestAlias:
    @pytest.mark.parametrize(
        "workflow_id, alias_name, exit_code",
        [
            ("b3b197b3-fdca-4647-9fd8-bf16d2cb734d", "breath", 0),  # adding alias
            ("a63aa10c-a43e-4ca7-9be9-c2d2aa08b96d", "", 0),  # removing alias
            ("-1", "dart", 0),  # testing relative Ids
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
        else:  # because command failed md5sum of mock and local should be the same
            assert hashlib.md5(open(local_workflow_database_tsv, 'rb').read()).hexdigest() == \
                   hashlib.md5(open(mock_workflow_database_tsv, 'rb').read()).hexdigest()
