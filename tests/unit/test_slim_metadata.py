import pytest

from cromshell.slim_metadata import command as slim_metadata_command


class TestSlimMetadata:
    """Test the slim metadata command functions"""

    @pytest.mark.parametrize(
        "test_keys, "
        "test_cromshell_config_options, "
        "test_slim_metadata_default_param, "
        "out_param, ",
        [
            # Cli keys should be used if provided
            (
                ["id"],
                {"slim_metadata_keys": ["key"]},
                ["submittedFiles"],
                ["id"],
            ),
            # Config keys from json should be used if cli empty
            (
                [],
                {"slim_metadata_keys": ["key"]},
                ["submittedFiles"],
                ["key"],
            ),
            # Slim metadata default should be used no keys found in cli or config
            (
                [],
                {"cromwell": ["stuff"]},
                ["submittedFiles"],
                ["submittedFiles"],
            ),
        ],
    )
    def test_resolve_and_return_metadata_keys(
        self,
        test_keys: list,
        test_cromshell_config_options: dict,
        test_slim_metadata_default_param: list,
        out_param: list,
    ):
        assert (
            slim_metadata_command.resolve_and_return_metadata_keys(
                cli_key=test_keys,
                cromshell_config_options=test_cromshell_config_options,
                config_slim_metadata_default_param=test_slim_metadata_default_param,
            )
            == out_param
        )
