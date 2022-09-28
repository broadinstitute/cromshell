import pytest
from pathlib import Path

from cromshell.utilities import config_options_file_utils as cofu


class TestConfigOptionsFileUtils:
    """Test the functions config_options_file_utils.py"""

    @pytest.mark.parametrize(
        "json_to_validate, validity", [
            ["config_options_file_utils/valid_json.json", True],
            ["config_options_file_utils/invalid_valid_json.json", False]
        ]
    )
    def test_valid_json(
        self, json_to_validate: str, validity: bool, mock_data_path: Path
    ) -> None:

        assert (
            cofu.valid_json(
                json_to_validate=mock_data_path.joinpath(json_to_validate),
            )
            == validity
        )
