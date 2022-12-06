import pytest

from cromshell.alias import command as alias_command


class TestAlias:
    """Test the alias command functions"""

    @pytest.mark.parametrize(
        "alias_name, alias_validity",
        [
            ["goodalias", False],
            ["-badalias", True],
            ["good-alias", False],
            ["goodalias-", False],
            ["bad alias", True],
            ["321", True],
        ],
    )
    def test_alias_is_invalid(self, alias_name: str, alias_validity: bool) -> None:
        assert alias_command.alias_is_invalid(alias_name=alias_name) is alias_validity

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
        mock_workflow_database_tsv,
    ) -> None:
        assert (
            alias_command.alias_exists(
                alias_name=alias_name, submission_file=str(mock_workflow_database_tsv)
            )
            is alias_existence
        )

    @pytest.mark.parametrize(
        "workflow_id, alias_exist, new_alias",
        [
            ["a63aa10c-a43e-4ca7-9be9-c2d2aa08b96d", True, "somealias"],
            ["a63aa10c-a43e-4ca7-9be9-c2d2aa08b96d", True, ""],
            ["b3b197b3-fdca-4647-9fd8-bf16d2cb734d", False, "somealias"],
            ["b3b197b3-fdca-4647-9fd8-bf16d2cb734d", False, ""],
        ],
    )
    #  'caplog' is pytest fixture
    def test_check_workflow_has_alias(
        self, workflow_id, alias_exist, new_alias, mock_workflow_database_tsv, caplog
    ) -> None:
        alias_command.check_workflow_has_alias(
            workflow_id=workflow_id,
            submission_file=mock_workflow_database_tsv,
            alias_name=new_alias,
        )
        for record in caplog.records:
            assert record.levelname == "WARNING"
            if alias_exist:
                if new_alias == "":
                    assert "will be removed." in caplog.text
                else:
                    assert f"will be replaced with '{new_alias}'" in caplog.text
