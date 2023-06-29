import json
import logging
import re
import shutil
from contextlib import nullcontext
from enum import Enum
from io import BytesIO
from pathlib import Path
from typing import BinaryIO, List, Union
from zipfile import ZIP_DEFLATED, ZipFile

import azure.core.exceptions
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from google.cloud import storage
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


def cat_file(file_path: str or Path, backend: str = None) -> str:
    """Prints the contents of a file to stdout. The path can either be a
    local file path, GCP file path, Azure file path, or AWS file path."""

    # Check if the file path is a local path
    if backend in BackendType.LOCAL.value:
        with open(file_path, "r") as file:
            file_contents = file.read()
    # Check if the file path is a GCP path
    elif backend in BackendType.GCP.value:
        file_contents = get_gcp_file_content(file_path)
    # Check if the file path is an Azure path
    elif backend in BackendType.AZURE.value:
        file_contents = get_azure_file_content(file_path)
    else:
        raise ValueError("Invalid file path")
    return file_contents


def get_gcp_file_content(file_path: str) -> str or None:
    """Returns the contents of a file located on GCP"""

    bucket_name, blob_path = file_path.split("//")[-1].split("/", 1)
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_path)

    return blob.download_as_string().decode("utf-8") if blob.exists() else None


def get_azure_file_content(file_path: str) -> str or None:
    """Returns the contents of a file located on Azure"""

    blob_service_client = BlobServiceClient(
        account_url=f"https://{get_az_storage_account()}.blob.core.windows.net",
        credential=DefaultAzureCredential(),
    )
    container_name, blob_path = file_path.split("/", 2)[1:]
    blob_client = blob_service_client.get_blob_client(
        container=container_name, blob=blob_path
    )
    blob_client.download_blob()

    try:
        if blob_client.exists():
            return blob_client.download_blob().readall().decode("utf-8")
        else:
            return None
    except azure.core.exceptions.HttpResponseError as e:
        if "AuthorizationPermissionMismatch" in str(e):
            LOGGER.error(
                "Caught an AuthorizationPermissionMismatch error, check that"
                "the Azure Storage Container has your account listed to have"
                "Storage Blob Data Contributor"
            )
        else:
            LOGGER.error(
                "Caught an error while trying to download the file from Azure: %s", e
            )
            raise e


def get_az_storage_account() -> str:
    """Returns the account name of the Azure storage account"""

    import cromshell.utilities.cromshellconfig as config

    try:
        return config.cromshell_config_options["azure_storage_account"]
    except KeyError:
        LOGGER.error(
            "An 'azure_storage_account' is required for this action but"
            "was not found in Cromshell configuration file. "
        )
        raise KeyError("Missing 'azure_storage_account' in Cromshell configuration")


def is_path_or_url_like(in_string: str) -> bool:
    """Check if the string is a path or url

    Args:
        in_string (str): The string to check for path or url like-ness
    """
    if (
        in_string.startswith("gs://")
        or in_string.startswith("/")
        or in_string.startswith("http://")
        or in_string.startswith("https://")
        or in_string.startswith("s3://")
    ):
        return True
    else:
        return False


def create_local_subdirectory(local_dir: str or Path, blob_path: str or Path) -> Path:
    """
    Creates a local subdirectory for a given blob path.
    A blob path is a path to a file in a GCS bucket.

    :param local_dir: Path to local directory
    :param blob_path: Path to blob in GCS bucket
    :return:
    """

    LOGGER.debug("Creating local subdirectory %s", blob_path)

    local_subdir = Path(local_dir) / Path(blob_path).parent
    Path.mkdir(local_subdir, exist_ok=True, parents=True)

    return local_subdir


def download_gcs_files(file_paths: list, local_dir: str or Path) -> None:
    """
    Downloads GCS files to local_dir while preserving directory structure

    Args:
        file_paths: list of GCS file paths to download
        local_dir: local directory to download files to
    """
    storage_client = storage.Client()

    for file_path in file_paths:
        # Extract bucket and blob path from file path
        LOGGER.debug("Downloading file %s", file_path)
        bucket_name, blob_path = file_path.split("//")[-1].split("/", 1)

        # Create local subdirectory if it doesn't exist
        local_subdir = create_local_subdirectory(
            local_dir=local_dir, blob_path=blob_path
        )

        # Download file to local subdirectory
        LOGGER.debug("Downloading file %s to %s", file_path, local_subdir)
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_path)
        if blob.exists():
            local_path = Path(local_subdir) / Path(blob_path).name
            blob.download_to_filename(local_path)

            LOGGER.debug("Downloaded file %s to %s", file_path, local_subdir)
        else:
            LOGGER.warning("File %s does not exist", file_path)


def download_azure_files(file_paths: list, local_dir: str or Path) -> None:
    """
    Downloads Azure files to local_dir while preserving directory structure

    Args:
        file_paths (list): List of Azure file paths to download
        local_dir (str): Local directory to download files to

    """

    default_credential = DefaultAzureCredential()
    account_url = f"https://{get_az_storage_account()}.blob.core.windows.net"

    for file_path in file_paths:
        # Extract container and blob path from file path
        LOGGER.debug("Downloading file %s", file_path)
        blob_service_client = BlobServiceClient(
            account_url=account_url, credential=default_credential
        )
        container_name, blob_path = file_path.split("/", 2)[1:]
        blob_client = blob_service_client.get_blob_client(
            container=container_name, blob=blob_path
        )

        # Create local subdirectory if it doesn't exist
        local_subdir = create_local_subdirectory(
            local_dir=local_dir, blob_path=blob_path
        )

        # Download file to local subdirectory
        LOGGER.debug("Downloading file %s to %s", file_path, local_subdir)
        if blob_client.exists():
            local_path = Path(local_subdir) / Path(blob_path).name
            with open(local_path, "wb") as file:
                file.write(blob_client.download_blob().readall())

            LOGGER.debug("Downloaded file %s to %s", file_path, local_subdir)
        else:
            LOGGER.warning("File %s does not exist", file_path)


class BackendType(Enum):
    """Enum to hold supported backend types"""

    # Backends listed here: https://cromwell.readthedocs.io/en/latest/backends/Backends/

    AWS = ("AWSBatch", "AWSBatchOld", "AWSBatchOld_Single", "AWSBatch_Single")
    AZURE = ("TES", "AzureBatch", "AzureBatch_Single")
    GA4GH = ("TES",)
    GCP = ("PAPIv2", "PAPIv2alpha1", "PAPIv2beta", "PAPIv2alpha")
    LOCAL = ("Local",)
    HPC = ("SGE", "SLURM", "LSF", "SunGridEngine", "HtCondor")


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


def get_color_for_status_key(status: str) -> str or None:
    """
    Helper method for getting the correct font color for
    a given execution status for a job (or none for unrecognized statuses)
    """

    from cromshell.utilities.cromshellconfig import color_output

    if not color_output:
        return None
    if "Done" in status:
        task_status_font = TextStatusesColor.TASK_COLOR_SUCCEEDED
    elif "Running" in status:
        task_status_font = TextStatusesColor.TASK_COLOR_RUNNING
    elif "RetryableFailure" in status:
        task_status_font = TextStatusesColor.TASK_COLOR_FAILING
    elif "Failed":
        task_status_font = TextStatusesColor.TASK_COLOR_FAILED

    return task_status_font
