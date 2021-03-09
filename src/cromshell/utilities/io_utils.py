import json
import logging
import os
import re
import shutil
from pathlib import Path

from termcolor import colored

LOGGER = logging.getLogger(__name__)


def dead_turtle():
    """Print Dead Turtle"""

    print(colored(r"    ,,    ,,     ,,      ", "red"))
    print(colored(r"    \‾\,-/‾/====/‾/,   ", "red"))
    print(colored(r"     \/=<‾><‾><‾><‾>-,  ", "red"))
    print(colored(r"     / (\‾\‾|‾/‾/‾/‾   ", "red"))
    print(colored(r"    \‾x/ ˙'-;-;-'˙      ", "red"))
    print(colored(r"     ‾‾                  ", "red"))


def turtle():
    """Print Alive Turtle"""

    print(colored(r"                  __         ", "green"))
    print(colored(r"       .,-;-;-,. /'_\       ", "green"))
    print(colored(r"     _/_/_/_|_\_\) /       ", "green"))
    print(colored(r"   '-<_><_><_><_>=/\        ", "green"))
    print(colored(r"     \`/_/====/_/-'\_\    ", "green"))
    print(colored(r'       ""     ""    ""       ', "green"))


def doomed_logo():
    """Print Doom """

    print(colored(r"=================     ===============     ===============   ========  ========", "red"))
    print(colored(r"\\ . . . . . . .\\   //. . . . . . .\\   //. . . . . . .\\  \\. . .\\// . . //", "red"))
    print(colored(r"||. . ._____. . .|| ||. . ._________________________. . .|| || . . .\/ . . .||", "red"))
    print(colored(r"|| . .||   ||. . || || . ./|  ,,    ,,     ,,      |\. . || ||. . . . . . . ||", "red"))
    print(colored(r"||. . ||   || . .|| ||. . ||  \‾\,-/‾/====/‾/,     || . .|| || . | . . . . .||", "red"))
    print(colored(r"|| . .||   ||. _-|| ||-_ .||   \/=<‾><‾><‾><‾>-,   ||. _-|| ||-_.|\ . . . . ||", "red"))
    print(colored(r"||. . ||   ||-'  || ||  `-||   / (\‾\‾|‾/‾/‾/‾     ||-'  || ||  `|\_ . .|. .||", "red"))
    print(colored(r"|| . _||   ||    || ||    ||  \‾x/ ˙'-;-;-'˙       ||    || ||   |\ `-_/| . ||", "red"))
    print(colored(r"||_-' ||  .|/    || ||    \|_______________________|/    || ||   | \  / |-_.||", "red"))
    print(colored(r"||    ||_-'      || ||      `-_||    || ||    ||_-'      || ||   | \  / |  `||", "red"))
    print(colored(r"||    `'         || ||         `'    || ||    `'         || ||   | \  / |   ||", "red"))
    print(colored(r"||            .===' `===.         .==='.`===.         .===' /==. |  \/  |   ||", "red"))
    print(colored(r"||         .=='   \_|-_ `===. .==='   _|_   `===. .===' _-|/   `==  \/  |   ||", "red"))
    print(colored(r"||      .=='    _-'    `-_  `='    _-'   `-_    `='  _-'   `-_  /|  \/  |   ||", "red"))
    print(colored(r"||   .=='    _-'          `-__\._-'         `-_./__-'         `' |. /|  |   ||", "red"))
    print(colored(r"||.=='    _-'                                                     `' |  /==.||", "red"))
    print(colored(r"=='    _-'                                                            \/   `==", "red"))
    print(colored(r"\   _-'                                                                `-_   /", "red"))
    print(colored(r".`''                                                                      ``'.", "red"))


def assert_required_file_is_not_empty(file_name: str, file_description: str):
    """Confirm the provided file exist and is not empty."""

    if file_name is None:
        LOGGER.info("%s was not provided", file_description)
        return
    if not Path(file_name).exists():
        LOGGER.error("ERROR: %s does not exist: %s", file_description, file_name)
        raise Exception("ERROR: %s does not exist: %s", file_description, file_name)
    else:
        if 0 == os.stat(file_name).st_size:
            LOGGER.error("ERROR: %s is empty: %s.", file_description, file_name)
            raise Exception("ERROR: %s is empty: %s.", file_description, file_name)


def is_workflow_id_valid(workflow_id: str):
    """Validates a workflow id"""

    pattern = re.compile("[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")

    return True if pattern.match(workflow_id) else False


def pretty_print_json(json_text: str):
    """Prints JSON String in a fancy way

    - json_text: content of the json, NOT json file path"""

    loaded_json = json.loads(json_text)
    print(json.dumps(loaded_json, indent=4, sort_keys=True))


def create_directory(dir_path: str, parents: bool = True, exist_ok: bool = False):
    """Creates a Directory
    - dir_path: full path to directory being created
    - parents: whether the new directory will need to be nested
                in new parent directories
    - exist_ok: whether to raise an exception if directory already exists"""

    try:
        Path.mkdir(Path(dir_path), parents=parents, exist_ok=exist_ok)
    except FileExistsError:
        LOGGER.error(
            f"Unable to create directory '{dir_path}' because directory already exists."
        )
        raise


def copy_files_to_directory(directory: str, input_files: []):
    """Copies files to specified directory"""

    for file in input_files:
        if file is not None:
            shutil.copy(file, directory)


def log_error_and_raise_exception(
    error_source: str, short_error_message: str, error_source_message: str
):
    """Prints out error message and url response
    to terminal. Also logs/raises error message and url response.

    - short_error_message: simple version of error message
    - error_source_message: error message given from source
    - error_source: Name of tool/package giving the error
    """

    LOGGER.error(f"Error: {short_error_message}")
    LOGGER.error(f"{error_source} Message: {error_source_message}")
    raise Exception(
        f"Error: {short_error_message}\n"
        f"{error_source} Message: {error_source_message}"
    )
