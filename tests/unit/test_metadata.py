import pytest

from cromshell.metadata import command as metadata_command


class TestMetadata:
    """Test the metadata command functions"""

    @pytest.mark.parametrize(
        "test_keys, test_keys_string_out",
        [
            (["id"], {"includeKey": ["id"]}),
            (["id", "status"], {"includeKey": ["id", "status"]}),
            (
                ["id", "status", "backendStatus"],
                {"includeKey": ["id", "status", "backendStatus"]},
            ),
        ],
    )
    def test_combine_keys_and_flags_combine_keys(self, test_keys, test_keys_string_out):
        assert (
            metadata_command.combine_keys_and_flags(
                list_of_keys=test_keys, exclude_keys=False, not_expand_subworkflow=False
            )
            == test_keys_string_out
        )

    @pytest.mark.parametrize(
        "test_keys",
        [
            [],  # Asserts failure on empty dictionary
            [""],  # Asserts failure on dictionary with empty string
            ["id", ""],  # Asserts failure on dictionary with empty element
        ],
    )
    def test_combine_keys_and_flags_empty_keys(self, test_keys):
        with pytest.raises(ValueError):
            metadata_command.combine_keys_and_flags(
                list_of_keys=test_keys, exclude_keys=False, not_expand_subworkflow=False
            ), "Should fail if given empty list."

    @pytest.mark.parametrize(
        "test_keys, test_expand_subworkflows, test_keys_string_out",
        [
            (["id"], False, {"includeKey": ["id"]}),
            (["id"], True, {"includeKey": ["id"], "expandSubWorkflows": "true"}),
        ],
    )
    def test_combine_keys_and_flags_subworkflows_flag(
        self, test_keys, test_expand_subworkflows, test_keys_string_out
    ):
        assert (
            metadata_command.combine_keys_and_flags(
                list_of_keys=test_keys,
                exclude_keys=False,
                not_expand_subworkflow=test_expand_subworkflows
            )
            == test_keys_string_out
        )

    @pytest.mark.parametrize(
        "test_keys, test_exclude_keys, test_keys_string_out",
        [
            (["id"], False, {"includeKey": ["id"]}),
            (["id"], True, {"excludeKey": ["id"]}),
        ],
    )
    def test_combine_keys_and_flags_exclude_keys_flag(
        self, test_keys, test_exclude_keys, test_keys_string_out
    ):
        assert (
            metadata_command.combine_keys_and_flags(
                list_of_keys=test_keys,
                exclude_keys=test_exclude_keys,
                not_expand_subworkflow=False
            )
            == test_keys_string_out
        )

    @pytest.mark.parametrize(
        "test_keys, "
        "test_cromshell_config_options, "
        "test_config_metadata_param, "
        "out_str, "
        "use_defaults",
        [
            # Cli keys should be used if provided
            (
                ["id"],
                {"metadata_keys": "key"},
                {'keys': ["submittedFiles"], 'includeKeys': False},
                ["id"],
                False,
            ),
            # Config keys should be used if cli empty
            (
                [],
                {"metadata_keys": ["key"]},
                {'keys': ["submittedFiles"], 'includeKeys': False},
                ["key"],
                False,
            ),
            # Metadata should be used by default if no keys found in cli or config
            (
                [],
                {"cromwell": ["stuff"]},
                {'keys': ["submittedFiles"], 'includeKeys': False},
                ["submittedFiles"],
                True,
            ),
        ],
    )
    def test_resolve_and_return_metadata_keys(
        self,
        test_keys,
        test_cromshell_config_options,
        test_config_metadata_param,
        out_str,
        use_defaults,
    ):
        assert (
            metadata_command.resolve_and_return_metadata_keys(
                cli_key=test_keys,
                cromshell_config_options=test_cromshell_config_options,
                config_metadata_param=test_config_metadata_param,
            )
            == out_str, use_defaults
        )
