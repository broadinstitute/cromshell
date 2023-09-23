import json
import logging
import re
import shutil
import tempfile
from contextlib import nullcontext
from io import BytesIO
from pathlib import Path
from typing import BinaryIO, List, Union
from zipfile import ZIP_DEFLATED, ZipFile

from pygments import formatters, highlight, lexers
from termcolor import colored

LOGGER = logging.getLogger(__name__)

workflow_id_pattern = re.compile(
    "[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}"
)


def dead_turtle() -> None:
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


def turtle() -> None:
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


def doomed_logo() -> None:
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


def assert_path_is_not_empty(path: Union[str, Path], description: str) -> None:
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


def has_nested_dependencies(wdl_path: str or Path) -> bool:
    """Determine if a WDL has any nested imports."""

    with open(wdl_path, "r") as rf:
        for line in rf:
            if line.startswith("import"):
                m = re.match(r'import "(.+)"', line)

                imported_wdl_name = m.group(1)
                if "../" in imported_wdl_name:
                    return True

    return False


def get_flattened_filename(tempdir: str, wdl_path: str or Path) -> Path:
    """Generate hyphen-separated path to use for flattened WDL file path.
    For example:
    tempdir: /path/2/tempdir/ and wdl_path: /dir/path/2/wdl.wdl
    returns: /path/2/tempdir/dir-path-2-wdl.wdl
    """

    p = Path(wdl_path)

    return Path(
        tempdir
        + "/"
        + re.sub("^-", "", re.sub("/", "-", str(p.parent)))
        + "-"
        + str(p.name)
    )


def flatten_nested_dependencies(
    tempdir: tempfile.TemporaryDirectory, wdl_path: str
) -> Path:
    """Flatten a WDL directory structure and rewrite imports accordingly.

    Return string representing the filesystem location of the rewritten WDL.

    tempdir: /path/2/tempdir/
    wdl_path: /dir/path/2/wdl.wdl
    returns: /path/2/tempdir/dir-path-2-wdl.wdl
    """

    p = Path(wdl_path)
    wdl_dir = p.parent

    new_wdl_path = get_flattened_filename(tempdir.name, wdl_path)

    with open(wdl_path, "r") as rf, open(new_wdl_path, "w") as wf:
        for line in rf:
            if line.startswith("import"):
                m = re.match(r'import "(.+)"', line)
                imported_wdl_name = m.group(1)
                imported_wdl_path = (Path(wdl_dir) / imported_wdl_name).resolve()
                import_line = re.sub(
                    imported_wdl_name,
                    Path(get_flattened_filename(tempdir.name, imported_wdl_path)).name,
                    line,
                )

                if " as " in line:
                    wf.write(import_line)
                else:
                    wf.write(
                        f'{import_line.strip()} as {re.sub(".wdl", "", Path(imported_wdl_path).name)}\n'
                    )

                flatten_nested_dependencies(tempdir, imported_wdl_path)
            else:
                wf.write(line)

    return new_wdl_path


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
    """
    Returns json with highlights
    :param formatted_json:
    :return:
    """
    return highlight(formatted_json, lexers.JsonLexer(), formatters.TerminalFormatter())


def pretty_print_json(format_json: str or dict, add_color: bool = None) -> None:
    """Prints JSON String in a fancy way

    Args:
    - json_text: valid json string or dictionary, NOT json file path
    - add_color: whether to add color to the json string
    """

    # Importing here to retrieve color_json value after being resolved by main()
    from cromshell.utilities.cromshellconfig import color_output as csc_color_json

    if add_color is None:
        add_color = csc_color_json

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
) -> None:
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
) -> None:
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


class TextStatusesColor:
    """Holds stdout formatting per workflow status"""

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


def get_color_for_status_key(status: str) -> str:
    """
    Helper method for getting the correct font color for
    a given execution status for a job (or none for unrecognized statuses)
    """

    task_status_font = None

    if "Done" in status:
        task_status_font = TextStatusesColor.TASK_COLOR_SUCCEEDED
    elif "Running" in status:
        task_status_font = TextStatusesColor.TASK_COLOR_RUNNING
    elif "RetryableFailure" in status:
        task_status_font = TextStatusesColor.TASK_COLOR_FAILING
    elif "Failed":
        task_status_font = TextStatusesColor.TASK_COLOR_FAILED

    return task_status_font
