import json
import logging
import os
import re
import shutil
from pathlib import Path

from termcolor import colored

LOGGER = logging.getLogger(__name__)

workflow_id_pattern = re.compile(
    "[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
)


def dead_turtle():
    """Print Dead Turtle"""

    print(
        colored(
            r"""
  ,,    ,,     ,,
  \‾\,-/‾/====/‾/,
   \/=<‾><‾><‾><‾>-,
   / (\‾\‾|‾/‾/‾/‾
  \‾x/ ˙'-;-;-'˙
   ‾‾
            """,
            "red",
        )
    )


def turtle():
    """Print Alive Turtle"""

    print(
        colored(
            r"""
                 __
      .,-;-;-,. /'_\
    _/_/_/_|_\_\) /
  '-<_><_><_><_>=/\
    `/_/====/_/-'\_\
     ""     ""    ""
            """,
            "green",
        )
    )


def doomed_logo():
    """Print Doom """

    print(
        colored(
            r"""
   =================     ===============     ===============   ========  ========
   \\ . . . . . . .\\   //. . . . . . .\\   //. . . . . . .\\  \\. . .\\// . . //
   ||. . ._____. . .|| ||. . ._________________________. . .|| || . . .\/ . . .||
   || . .||   ||. . || || . ./|  ,,    ,,     ,,      |\. . || ||. . . . . . . ||
   ||. . ||   || . .|| ||. . ||  \‾\,-/‾/====/‾/,     || . .|| || . | . . . . .||
   || . .||   ||. _-|| ||-_ .||   \/=<‾><‾><‾><‾>-,   ||. _-|| ||-_.|\ . . . . ||
   ||. . ||   ||-'  || ||  `-||   / (\‾\‾|‾/‾/‾/‾     ||-'  || ||  `|\_ . .|. .||
   || . _||   ||    || ||    ||  \‾x/ ˙'-;-;-'˙       ||    || ||   |\ `-_/| . ||
   ||_-' ||  .|/    || ||    \|_______________________|/    || ||   | \  / |-_.||
   ||    ||_-'      || ||      `-_||    || ||    ||_-'      || ||   | \  / |  `||
   ||    `'         || ||         `'    || ||    `'         || ||   | \  / |   ||
   ||            .===' `===.         .==='.`===.         .===' /==. |  \/  |   ||
   ||         .=='   \_|-_ `===. .==='   _|_   `===. .===' _-|/   `==  \/  |   ||
   ||      .=='    _-'    `-_  `='    _-'   `-_    `='  _-'   `-_  /|  \/  |   ||
   ||   .=='    _-'          `-__\._-'         `-_./__-'         `' |. /|  |   ||
   ||.=='    _-'                                                     `' |  /==.||
   =='    _-'                                                            \/   `==
   \   _-'                                                                `-_   /
   .`''                                                                      ``'.
            """,
            "red",
        )
    )


def assert_file_is_not_empty(file_path: str, file_description: str):
    """Confirm the provided file exist and is not empty."""

    if not Path(file_path).exists():
        LOGGER.error("ERROR: %s does not exist: %s", file_description, file_path)
        raise FileExistsError(
            "ERROR: %s does not exist: %s", file_description, file_path
        )
    elif os.stat(file_path).st_size == 0:
        LOGGER.error("ERROR: %s is empty: %s.", file_description, file_path)
        raise EOFError("ERROR: %s is empty: %s.", file_description, file_path)


def is_workflow_id_valid(workflow_id: str):
    """Validates a workflow id"""

    return True if workflow_id_pattern.match(workflow_id) else False


def pretty_print_json(json_text: str):
    """Prints JSON String in a fancy way

    - json_text: content of the json, NOT json file path"""

    loaded_json = json.loads(json_text)
    print(json.dumps(loaded_json, indent=4, sort_keys=True))


def create_directory(
    dir_path: str or Path, parents: bool = True, exist_ok: bool = False
):
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


def copy_files_to_directory(directory: str or Path, input_files: list or str):
    """Copies files to specified directory"""

    # check dir exists
    if not Path(directory).exists():
        raise FileNotFoundError(f"Directory '{directory}' does not exist")

    if type(input_files) is list:
        for file in input_files:
            if file is not None:
                if not Path(file).exists():
                    raise FileNotFoundError(f"Directory '{file}' does not exist")
                shutil.copy(file, directory)
    else:
        if not Path(input_files).exists():
            raise FileNotFoundError(f"Directory '{input_files}' does not exist")
        shutil.copy(input_files, directory)


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
