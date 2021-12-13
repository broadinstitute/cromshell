import csv
import fileinput
import json
import logging
import os
import re
import shutil
from pathlib import Path

from pygments import formatters, highlight, lexers
from termcolor import colored

LOGGER = logging.getLogger(__name__)

workflow_id_pattern = re.compile(
    "[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}"
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
    """Print Doom"""

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


def assert_file_is_not_empty(file_path: str or Path, file_description: str):
    """Confirm the provided file exist and is not empty."""

    if not Path(file_path).exists():
        LOGGER.error("ERROR: %s does not exist: %s", file_description, file_path)
        raise FileExistsError(f"ERROR: {file_description} does not exist: {file_path}")
    if os.stat(file_path).st_size == 0:
        LOGGER.error("ERROR: %s is empty: %s.", file_description, file_path)
        raise EOFError(f"ERROR: {file_description} is empty: {file_path}.")


def is_workflow_id_valid(workflow_id: str):
    """Validates a workflow id"""

    if workflow_id == "":
        raise ValueError("Empty String")

    return workflow_id_pattern.match(workflow_id)


def color_json(formatted_json: str) -> str:
    return highlight(formatted_json, lexers.JsonLexer(), formatters.TerminalFormatter())


def pretty_print_json(format_json: str or dict, add_color: bool = False):
    """Prints JSON String in a fancy way

    - json_text: valid json string or dictionary, NOT json file path"""

    if format_json is type(str):
        loaded_json = json.loads(format_json)
    else:
        loaded_json = format_json
    pretty_json = json.dumps(loaded_json, indent=4, sort_keys=True)
    if add_color:
        print(color_json(pretty_json))
    else:
        print(pretty_json)


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
            "Unable to create directory '%s' because directory already exists.",
            dir_path,
        )
        raise


def copy_files_to_directory(directory: str or Path, input_files: list or str):
    """Copies files to specified directory"""

    # check dir exists
    if not Path(directory).exists():
        raise FileNotFoundError(f"Directory '{directory}' does not exist")

    if isinstance(input_files, list):
        for file in input_files:
            if file is not None:
                if not Path(file).exists():
                    raise FileNotFoundError(f"Directory '{file}' does not exist")
                shutil.copy(file, directory)
    else:
        if not Path(input_files).exists():
            raise FileNotFoundError(f"Directory '{input_files}' does not exist")
        shutil.copy(input_files, directory)


def update_all_workflow_database_tsv(
    workflow_database_path: str,
    workflow_id: str,
    column_to_update: str,
    update_value: str,
) -> None:
    """
    Updates the all_workflow_database_tsv for a given workflow_id and column
    :param workflow_database_path: Path to all_workflow_database tsv file
    :param workflow_id: Hexadecimal identifier of workflow submission
    :param column_to_update:["RUN_ID", "STATUS", "ALIAS", "WDL_NAME", "CROMWELL_SERVER"]
    :param update_value: Value of the cell to update
    :return:
    """

    available_columns = ["STATUS", "ALIAS", "WDL_NAME", "CROMWELL_SERVER"]
    if column_to_update not in available_columns:
        raise ValueError(
            f"Invalid column_to_update: '{column_to_update}'. "
            f"Expected one of: '{available_columns}'"
        )

    # Update config.submission_file:
    with fileinput.FileInput(
        workflow_database_path, inplace=True, backup=".bak"
    ) as csv_file:
        reader = csv.DictReader(csv_file, delimiter="\t")
        print("\t".join(reader.fieldnames))
        for row in reader:
            if row["RUN_ID"] == workflow_id:
                row[column_to_update] = update_value
                print("\t".join(x for x in row.values() if x))
            else:
                print("\t".join(x for x in row.values() if x))
