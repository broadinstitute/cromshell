import json
import logging
from pathlib import Path

LOGGER = logging.getLogger(__name__)


CONFIG_FILE_TEMPLATE = {"cromwell_server": "str", "requests_timeout": "int"}


def valid_json(json_to_validate: str or Path, json_is_file_path: bool = True) -> bool:
    """

    :param json_is_file_path:
    :param json_to_validate:
    :return:
    """

    # The json.load() is used to read the JSON document from file and
    # The json.loads() is used to convert the JSON String document
    # into the Python dictionary.

    try:
        if json_is_file_path:
            with open(json_to_validate, "r") as f:
                json.load(f)

        else:
            json.loads(str(json_to_validate))
    except ValueError:
        return False

    return True


def validate_json_schema(loaded_json_file: dict, json_schema: dict) -> None:
    """

    :param loaded_json_file:
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

    for key in loaded_json_file:
        if key not in json_schema:
            LOGGER.error(
                "JSON key: '%s' is not an accepted option. "
                "The available options are: %s",
                key,
                list(json_schema.keys()),
            )
            raise KeyError(
                f"ERROR: key: '{key}' is not an found in the provided JSON schema"
            )

        if type(loaded_json_file[key]) != json_value_types[json_schema[key]]:
            LOGGER.error(
                "The expected value type for option '%s' is '%s', but %s was provided.",
                key,
                json_schema[key],
                type(loaded_json_file[key]),
            )
            raise ValueError(
                f"The expected value type for option '{key}' is "
                f"'{json_schema[key]}', but {type(loaded_json_file[key])} "
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
            "The provided file: %s failed JSON validation.", config_options_file
        )
        raise ValueError(
            f"ERROR: The provided file: {config_options_file} failed JSON validation."
        )

    with open(config_options_file, "r") as f:
        validate_json_schema(
            loaded_json_file=json.load(f), json_schema=CONFIG_FILE_TEMPLATE
        )
