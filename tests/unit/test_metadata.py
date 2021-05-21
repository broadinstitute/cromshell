import pytest

from cromshell.metadata import command as metadata_command


class TestMetadata:
    """Test the metadata command functions"""

    @pytest.mark.parametrize(
        "test_keys, test_keys_string_out",
        [
            (["id"], "includeKey=id"),
            (["id", "status"], "includeKey=id&includeKey=status"),
            (
                ["id", "status", "backendStatus"],
                "includeKey=id&includeKey=status&includeKey=backendStatus"
            ),
        ]
    )
    def test_process_keys(self, test_keys, test_keys_string_out):
        assert metadata_command.process_keys(
            test_keys,
            not_expand_subworkflow=False
        ) == test_keys_string_out

    @pytest.mark.parametrize(
        "test_keys",
        [
            [],  # Asserts failure on empty dictionary
            [""],  # Asserts failure on dictionary with empty string
            ["id", ""],  # Asserts failure on dictionary with empty element
        ]
    )
    def test_empty_process_keys(self, test_keys):
        with pytest.raises(ValueError):
            metadata_command.process_keys(
                list_of_keys=test_keys, not_expand_subworkflow=False
            ), "Should fail if given empty list."

    @pytest.mark.parametrize(
        "test_keys, test_expand_subworkflows, test_keys_string_out",
        [
            (["id"], False, "includeKey=id"),
            (["id"], True, "includeKey=id&expandSubWorkflows=true"),
        ]
    )
    def test_process_keys_expand_subworkflows_flag(
            self,
            test_keys,
            test_expand_subworkflows,
            test_keys_string_out
    ):
        assert metadata_command.process_keys(
            test_keys,
            not_expand_subworkflow=test_expand_subworkflows
        ) == test_keys_string_out

    @pytest.mark.parametrize(
        "test_keys, test_cromshell_config_options, test_config_metadata_param, out_str",
        [
            # Cli keys should be used if provided
            (
                ["id"],
                {"metadata_keys": "key"},
                "Metadata_Keys_Constant",
                "includeKey=id"
            ),
            # Config keys should be used if cli empty
            (
                [],
                {"metadata_keys": ["key"]},
                "Metadata_Keys_Constant",
                "includeKey=key"
            ),
            # Metadata should be used by default if no keys found in cli or config
            (
                [],
                {"cromwell": ["stuff"]},
                "includeKey=Metadata_Keys_Constant",
                "includeKey=Metadata_Keys_Constant"
            ),
        ]
    )
    def test_resolve_and_return_metadata_keys(
            self,
            test_keys,
            test_cromshell_config_options,
            test_config_metadata_param,
            out_str,
    ):
        assert metadata_command.resolve_and_return_metadata_keys(
            cli_key=test_keys,
            cromshell_config_options=test_cromshell_config_options,
            config_metadata_param=test_config_metadata_param,
            not_expand_subworkflow=False
        ) == out_str
