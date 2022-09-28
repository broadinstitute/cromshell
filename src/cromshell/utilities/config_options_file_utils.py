import json
import logging
from pathlib import Path

LOGGER = logging.getLogger(__name__)


CONFIG_FILE_TEMPLATE = {"cromwell_server": "str", "requests_timeout": "int"}


def valid_json(json_to_validate: str or Path) -> bool:
    """

    :param json_to_validate:
    :return:
    """
    try:
        try:
            with open(json_to_validate, "r") as f:
                json.load(f)
        except FileNotFoundError:
            json.loads(json_to_validate)
    except ValueError:
        return False

    return True


def check_config_file_content(config_file: dict, config_file_template: dict = None):
    """

    :param config_file:
    :param config_file_template:
    :return:
    """
    if config_file_template is None:
        config_file_template = CONFIG_FILE_TEMPLATE

    py_var_types = {
        "int": int,
        "Int": int,
        "float": float,
        "str": str,
        "String": str,
    }

    for key in config_file:
        assert key in config_file_template, f"key: '{key}' is not an accepted option"
        assert type(config_file[key]) is py_var_types[config_file_template[key]], (
            f"The value type for option '{key}' is expected to be "
            f"'{config_file_template[key]}', but {type(config_file[key])} was provided."
        )


def validate_cromshell_config_options_file(config_options_file: str):
    """

    :param config_options_file:
    :return:
    """

    assert valid_json(
        json_to_validate=config_options_file
    ), f"The provided file: {config_options_file} failed JSON validation."

    with open(config_options_file, "r") as f:
        check_config_file_content(config_file=json.load(f))
