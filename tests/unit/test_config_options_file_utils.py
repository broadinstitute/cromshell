from pathlib import Path

import pytest
from cromshell.utilities import config_options_file_utils as cofu


class TestConfigOptionsFileUtils:
    """Test the functions in config_options_file_utils.py"""

    @pytest.mark.parametrize(
        "json_to_validate, json_is_file_path, validity",
        [
            ["config_options_file_utils/valid.json", True, True],
            ["config_options_file_utils/invalid.json", True, False],
            [
                '{"cromwell_server": "http://localhost:8000", "requests_timeout": 5}',
                False,
                True,
            ],
            [
                '{"cromwell_serverttp://localhost:8000", "requests_tim 5}',
                False,
                False,
            ],
        ],
    )
    def test_valid_json(
        self,
        json_to_validate: str,
        validity: bool,
        json_is_file_path: bool,
        mock_data_path: Path,
    ) -> None:

        if json_is_file_path:
            assert (
                cofu.valid_json(
                    json_to_validate=mock_data_path.joinpath(json_to_validate),
                    json_is_file_path=json_is_file_path,
                )
                == validity
            )
        else:
            assert (
                cofu.valid_json(
                    json_to_validate=json_to_validate,
                    json_is_file_path=json_is_file_path,
                )
                == validity
            )

    @pytest.mark.parametrize(
        "config_file_args, validity, error_type",
        [
            [
                {"cromwell_server": "http://localhost:8000", "requests_timeout": 5},
                True,
                None,
            ],
            # bad value
            [
                {"cromwell_server": 3, "requests_timeout": 2},
                False,
                ValueError,
            ],
            # bad key
            [
                {"foo": "http://localhost:8000", "requests_timeout": 5},
                False,
                KeyError,
            ],
            # bad key and value
            [
                {"foo": 0, "requests_timeout": 5},
                False,
                KeyError,
            ],
        ],
    )
    def test_validate_json_schema(
        self, config_file_args: dict, validity: bool, error_type
    ):

        if validity:
            cofu.validate_json_schema(
                loaded_json=config_file_args, json_schema=cofu.CONFIG_FILE_TEMPLATE
            )
        else:
            with pytest.raises(error_type):
                cofu.validate_json_schema(
                    loaded_json=config_file_args,
                    json_schema=cofu.CONFIG_FILE_TEMPLATE,
                )

    @pytest.mark.parametrize(
        "json_to_validate, validity",
        [
            ["config_options_file_utils/valid.json", True],
            ["config_options_file_utils/invalid.json", False],
        ],
    )
    def test_validate_cromshell_config_options_file(
        self, json_to_validate, validity, mock_data_path: Path
    ):
        if validity:
            cofu.validate_cromshell_config_options_file(
                config_options_file=mock_data_path.joinpath(json_to_validate)
            )
        else:
            with pytest.raises(ValueError):
                cofu.validate_cromshell_config_options_file(
                    config_options_file=mock_data_path.joinpath(json_to_validate)
                )
