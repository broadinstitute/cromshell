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
    def test_format_metadata_params(self, test_keys, test_keys_string_out):
        assert (
            metadata_command.format_metadata_params(
                list_of_keys=test_keys, exclude_keys=False, expand_subworkflow=False
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
    def test_format_metadata_params_empty_keys(self, test_keys):
        with pytest.raises(ValueError):
            metadata_command.format_metadata_params(
                list_of_keys=test_keys, exclude_keys=False, expand_subworkflow=False
            ), "Should fail if given empty list."

    @pytest.mark.parametrize(
        "test_keys, test_expand_subworkflows, test_keys_string_out",
        [
            (["id"], False, {"includeKey": ["id"]}),
            (["id"], True, {"includeKey": ["id"], "expandSubWorkflows": "true"}),
        ],
    )
    def test_format_metadata_params_subworkflows_flag(
        self, test_keys, test_expand_subworkflows, test_keys_string_out
    ):
        assert (
            metadata_command.format_metadata_params(
                list_of_keys=test_keys,
                exclude_keys=False,
                expand_subworkflow=test_expand_subworkflows,
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
    def test_format_metadata_params_exclude_keys_flag(
        self, test_keys, test_exclude_keys, test_keys_string_out
    ):
        assert (
            metadata_command.format_metadata_params(
                list_of_keys=test_keys,
                exclude_keys=test_exclude_keys,
                expand_subworkflow=False,
            )
            == test_keys_string_out
        )
