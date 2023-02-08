import json
import logging
from pathlib import Path
from typing import Union

LOGGER = logging.getLogger(__name__)


CONFIG_FILE_TEMPLATE = {
    "cromwell_server": "str",
    "requests_timeout": "int",
    "gcloud_token_email": "str",
    "referer_header_url": "str",
    "bq_cost_table": "str"
}


class MissingConfigParametersException(Exception):
    """Raised when Cromshell Config file is missing required parameters"""
    pass


def valid_json(json_to_validate: str or Path, json_is_file_path: bool = True) -> bool:
    """

    :param json_is_file_path:
    :param json_to_validate:
    :return:
    """

    # The json.load() used for json files, and json.loads() used for JSON String.

    try:
        if json_is_file_path:
            with open(json_to_validate, "r") as f:
                json.load(f)

        else:
            json.loads(str(json_to_validate))
    except ValueError:
        return False

    return True


def validate_json_schema(loaded_json: dict, json_schema: dict) -> None:
    """
    Check if the keys provided in Cromshell's configurations file match the
    template schema, if not warn the user. Also check if the type of the key value
    matches the expected value type.

    :param loaded_json:
    :param json_schema:
    :return:
    """

    json_value_types = {
        "int": int,
        "Int": int,
        "float": float,
        "Float": float,
        "str": str,
        "String": str,
        "list": list,
        "List": list,
        "Array": list,
        "dict": dict,
        "Dict": dict,
    }

    for key in loaded_json:
        if key not in json_schema:
            LOGGER.warning(
                "JSON key: '%s' is not an accepted option and will NOT be used "
                "by Cromshell. The available options are: %s",
                key,
                list(json_schema.keys()),
            )
        else:
            if not isinstance(loaded_json[key], json_value_types[json_schema[key]]):
                LOGGER.error(
                    "Expected value type for option '%s' is '%s', but %s was provided.",
                    key,
                    json_schema[key],
                    type(loaded_json[key]),
                )
                raise ValueError(
                    f"Expected value type for option '{key}' is "
                    f"'{json_schema[key]}', but {type(loaded_json[key])} "
                    f"was provided."
                )


def validate_cromshell_config_options_file(config_options_file: Path) -> None:
    """

    :param config_options_file:
    :return:
    """

    LOGGER.info("Checking Cromshell Config Options File.")

    if not valid_json(json_to_validate=config_options_file):
        LOGGER.error(
            "The provided file: %s failed JSON format validation. Check that"
            "the file adheres to basic JSON formatting rules.",
            config_options_file,
        )
        raise ValueError(
            f"ERROR: The provided file: {config_options_file} failed JSON format"
            "validation."
        )

    with open(config_options_file, "r") as f:
        validate_json_schema(loaded_json=json.load(f), json_schema=CONFIG_FILE_TEMPLATE)


def check_key_is_configured(
    key_to_check: str, config_options: dict, config_file_path: str
) -> Union[str, int, dict, list]:
    if key_to_check not in config_options:
        LOGGER.error(f"Cromshell config file is missing Key '{key_to_check}'. "
                     f"Add Key and value to config file: {config_file_path}"
                     )
        raise MissingConfigParametersException("Cromshell config file is missing Key "
                                               f"'{key_to_check}'. Add Key and value "
                                               f"to config file: {config_file_path}"
                                               )
    return config_options.get(key_to_check)
