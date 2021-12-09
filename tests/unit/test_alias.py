import csv
import shutil
from pathlib import Path

import pytest

from cromshell.alias import command as alias_command


@pytest.fixture
def mock_data_path():
    return Path(__file__).parent.joinpath("mock_data/")


@pytest.fixture
def submission_file(mock_data_path):
    return mock_data_path.joinpath("all.workflow.database.tsv")


class TestAlias:
    """Test the alias command functions"""

    @pytest.mark.parametrize(
        "alias_name, alias_validity",
        [
            ["goodalias", True],
            ["-badalias", False],
            ["good-alias", True],
            ["goodalias-", True],
            ["bad alias", False],
            ["321", False],
        ],
    )
    def test_alias_is_valid(self, alias_name: str, alias_validity: bool) -> None:
        assert alias_command.alias_is_valid(alias_name=alias_name) is alias_validity

    @pytest.mark.parametrize(
        "alias_name, alias_existence",
        [
            ["wombat", True],
            ["foo", False],
            ["Failed", False],
        ],
    )
    def test_alias_exists(
        self,
        alias_name: str,
        alias_existence: bool,
        submission_file,
    ) -> None:
        assert (
            alias_command.alias_exists(
                alias_name=alias_name, submission_file=str(submission_file)
            )
            is alias_existence
        )

    @pytest.mark.parametrize(
        "workflow_id, alias_existence",
        [
            ["a63aa10c-a43e-4ca7-9be9-c2d2aa08b96d", True],
            ["b3b197b3-fdca-4647-9fd8-bf16d2cb734d", False],
        ],
    )
    #  'caplog' is pytest fixture
    def test_check_workflow_has_alias(
        self, workflow_id, alias_existence, submission_file, caplog
    ) -> None:
        alias_command.check_workflow_has_alias(
            workflow_id=workflow_id, submission_file=submission_file
        )
        for record in caplog.records:
            assert record.levelname == "WARNING"
            if alias_existence:
                assert "Workflow already has alias, its current alias" in caplog.text

    # 'tmp_path' is a default pytest fixture
    def test_set_alias_for_workflow_id(
        self, mock_data_path, submission_file, tmp_path
    ) -> None:

        alias_name = "wonderwoman"
        workflow_id = "b3b197b3-fdca-4647-9fd8-bf16d2cb734d"
        temp_submission_file = str(tmp_path) + "/submission_file.text"

        # Copy submission file template to temp dir
        shutil.copyfile(submission_file, temp_submission_file)

        # Run function to change alias using the temp submission file
        alias_command.set_alias_for_workflow_id(
            alias_name=alias_name,
            workflow_id=workflow_id,
            submission_file_path=temp_submission_file,
        )

        # Open the temp submission file that was recently updated and compare the last
        # the alias name of the workflow id
        with open(temp_submission_file, "r") as csv_file:
            reader = csv.DictReader(csv_file, delimiter="\t")
            for row in reader:
                if row["RUN_ID"] == workflow_id:
                    assert row["ALIAS"] == alias_name
