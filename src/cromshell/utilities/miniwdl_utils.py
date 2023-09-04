import io
import logging
import tempfile
import zipfile
from contextlib import redirect_stdout
from os import listdir
from pathlib import Path

from cromshell import log
from cromshell.utilities import io_utils
from cromshell.utilities.io_utils import dead_turtle

LOGGER = logging.getLogger(__name__)


class ValidationFailedError(Exception):
    pass


def miniwdl_validate_wdl(
    wdl: Path,
    dependencies: str or Path = None,
    strict: bool = False,
    suppress=None,
    show_warnings: bool = True,
) -> int:
    """Validates a WDL file.

    Args:
      wdl: The path to the WDL file.
      dependencies: A list of paths to the WDL file's dependencies.
      strict: Whether to be strict about the WDL file's syntax.
      suppress: A list of errors to suppress.
      show_warnings: Whether to show warnings.

    Returns:
      0 if the WDL file is valid, 1 otherwise.
    """

    LOGGER.debug("Validating WDL file with miniwdl.")
    if suppress is None:
        suppress = []
    if dependencies is None:
        dependencies = []

    resolved_dependencies = resolve_wdl_dependencies(dependencies)

    LOGGER.debug(f"WDL dependencies location: {resolved_dependencies}")
    LOGGER.debug(f"Contents dependencies location: {listdir(resolved_dependencies)}")

    try:
        f = io.StringIO()
        with redirect_stdout(f):
            # Importing miniwdl.check here to help with stdout redirection
            from WDL.CLI import check as miniwdl_check

            miniwdl_check(
                uri=[str(wdl)],
                path=[resolved_dependencies],
                strict=strict,
                suppress=",".join([str(item) for item in suppress]),  # Turn into string
            )

        captured_outputs = f.getvalue()
    except Exception as exn:
        # Importing miniwdl.print_error here to help with stdout redirection
        from WDL.CLI import print_error as miniwdl_print_error

        log.display_logo(logo=dead_turtle)
        miniwdl_print_error(exn)

        if logging.getLogger().level == logging.DEBUG:
            LOGGER.error(exn)
            raise ValidationFailedError(exn)

        return 1

    if show_warnings:
        print(captured_outputs)

    return 0


def resolve_wdl_dependencies(dependencies: str or Path) -> str or Path:
    """Resolves the dependencies of a WDL file. If the dependencies are a ZIP file,
    it will be extracted to a temporary directory and the path to the temp directory
    will be returned. If the `dependencies` is a directory,
    it will be checked if it contains a WDL file. If it does, the path to the
    directory will be returned. Otherwise, an error will be raised.

    Args:
        dependencies: A list of paths to the WDL file's dependencies.
    """

    resolved_dependencies = []

    if Path(dependencies).is_file():
        temp_dir = tempfile.mkdtemp(prefix="cromshell_")
        with zipfile.ZipFile(dependencies, "r") as zip_ref:
            zip_ref.extractall(temp_dir)
        io_utils.check_if_dir_contains_wdl(temp_dir)
        resolved_dependencies = temp_dir
    elif Path(dependencies).is_dir():
        io_utils.check_if_dir_contains_wdl(dependencies)
        resolved_dependencies = dependencies
    else:
        raise FileNotFoundError(
            f"Dependencies {dependencies} is not a directory or a ZIP file."
        )

    return resolved_dependencies
