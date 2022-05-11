import csv
import fileinput
import json
import logging
import re
import shutil
from contextlib import nullcontext
from io import BytesIO
from pathlib import Path
from typing import BinaryIO, List, Union
from zipfile import ZIP_DEFLATED, ZipFile

from pygments import formatters, highlight, lexers
from termcolor import colored

from cromshell.utilities import submissions_file_utils

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


def assert_path_is_not_empty(path: Union[str, Path], description: str):
    """Confirm the provided file or directory exist and is not empty."""

    if not Path(path).exists():
        LOGGER.error("ERROR: %s does not exist: %s", description, path)
        raise FileExistsError(f"ERROR: {description} does not exist: {path}")
    if Path(path).is_dir():
        if not Path(path).iterdir():
            LOGGER.error("ERROR: %s is empty: %s.", description, path)
            raise EOFError(f"ERROR: {description} is empty: {path}.")
    else:
        if Path(path).stat().st_size == 0:
            LOGGER.error("ERROR: %s is empty: %s.", description, path)
            raise EOFError(f"ERROR: {description} is empty: {path}.")


def open_or_zip(path: Union[str, Path, None]) -> Union[nullcontext, BytesIO, BinaryIO]:
    """Return a context that may be used for reading the contents from the path.

    If path is a directory returns the contents as an in memory zip file.
    """

    if not path:
        return nullcontext()

    path = Path(path)
    if path.is_dir():
        return zip_dir(path)
    else:
        return path.open("rb")


def zip_dir(directory: Path) -> BytesIO:
    """Zip the directory to an in memory BytesIO."""

    zip_buffer = BytesIO()
    base = Path(directory)
    LOGGER.debug("Zipping directory: %s", directory)
    # Based off of https://stackoverflow.com/questions/2463770/python-in-memory-zip-library
    with ZipFile(zip_buffer, "a", ZIP_DEFLATED, False) as zip_file:
        for child in base.iterdir():
            add_to_zip(zip_file, base, child)

    zip_buffer.seek(0)
    return zip_buffer


def add_to_zip(zip_file: ZipFile, base: Path, path: Path) -> None:
    """Add the path to the zip file relative to the base."""

    relative_path = path.relative_to(base)
    LOGGER.debug("Zipping: %s", relative_path)
    zip_file.write(path, relative_path)

    if path.is_dir():
        for child in path.iterdir():
            add_to_zip(zip_file, base, child)


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


def copy_files_to_directory(
    directory: Union[str, Path],
    inputs: Union[List[Union[str, Path, None]], Union[str, Path, None]],
):
    """Copies files to specified directory"""

    # check dir exists
    if not Path(directory).exists():
        raise FileNotFoundError(f"Directory '{directory}' does not exist")

    if not inputs:
        pass
    elif isinstance(inputs, list):
        for file in inputs:
            copy_files_to_directory(directory, file)
    elif not Path(inputs).exists():
        raise FileNotFoundError(f"File '{inputs}' does not exist")
    elif Path(inputs).is_dir():
        subdirectory = Path(directory) / Path(inputs).name
        shutil.copytree(inputs, subdirectory, copy_function=shutil.copy)
    else:
        shutil.copy(inputs, directory)


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
    :param column_to_update:["STATUS", "ALIAS"]
    :param update_value: Value of the cell to update
    :return:
    """

    available_columns = [
        column.value for column in submissions_file_utils.MutableSubmissionFileHeader
    ]
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
        print("\t".join(reader.fieldnames))  # print statement rewrites file header
        for row in reader:
            if row["RUN_ID"] == workflow_id:
                row[column_to_update] = update_value
                print("\t".join(x for x in row.values() if x))  # writes row with update
            else:
                print("\t".join(x for x in row.values() if x))  # rewrites row


class TextStatusesColor:
    """Enum to hold all possible status of workflow"""

    COLOR_NORM = {"color": None, "attrs": None}
    COLOR_UNDERLINED = {"color": None, "attrs": ["underline"]}
    COLOR_FAILED = "\033[1;37;41m"
    COLOR_DOOMED = "\033[1;31;47m"
    COLOR_SUCCEEDED = "\033[1;30;42m"
    COLOR_RUNNING = "\033[0;30;46m"
    COLOR_ABORTED = "\033[0;30;43m"

    TASK_COLOR_RUNNING = "blue"
    TASK_COLOR_SUCCEEDED = "green"
    TASK_COLOR_FAILING = "yellow"
    TASK_COLOR_FAILED = "red"


def get_color_for_status_key(status):
    """Helper method for getting the correct font color for a given execution status for a job (or none for
    unrecognized statuses) """
    if "Done" in status:
        task_status_font = TextStatusesColor.TASK_COLOR_SUCCEEDED
    elif "Running" in status:
        task_status_font = TextStatusesColor.TASK_COLOR_RUNNING
    elif "RetryableFailure" in status:
        task_status_font = TextStatusesColor.TASK_COLOR_FAILING
    elif "Failed":
        task_status_font = TextStatusesColor.TASK_COLOR_FAILED
    else:
        task_status_font = None
    return task_status_font