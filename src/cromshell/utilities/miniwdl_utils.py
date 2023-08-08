import logging
from pathlib import Path

from WDL import CLI as miniwdlCLI
from WDL import Error as miniwdlError

from cromshell import log
from cromshell.utilities.io_utils import dead_turtle

LOGGER = logging.getLogger(__name__)


class ValidationFailedError(Exception):
    pass


def miniwdl_validate_wdl(
    wdl: Path, dependencies: tuple = (), strict: bool = False, suppress=None
) -> int:
    """Validates a WDL file.

    Args:
      wdl: The path to the WDL file.
      dependencies: A list of paths to the WDL file's dependencies.
      strict: Whether to be strict about the WDL file's syntax.
      suppress: A list of errors to suppress.

    Returns:
      0 if the WDL file is valid, 1 otherwise.
    """
    if suppress is None:
        suppress = []
    LOGGER.debug("Validating WDL file with miniwdl.")

    for dep in dependencies:
        Path(dep).resolve(strict=True)

    try:
        miniwdlCLI.check(
            uri=[str(wdl)],
            path=list(dependencies),
            strict=strict,
            suppress=",".join([str(item) for item in suppress]),  # Turn into string
        )
    except (
        miniwdlError.SyntaxError,
        miniwdlError.ImportError,
        miniwdlError.ValidationError,
        miniwdlError.MultipleValidationErrors,
    ) as exn:
        log.display_logo(logo=dead_turtle)

        miniwdlCLI.print_error(exn)

        if logging.getLogger().level == logging.DEBUG:
            LOGGER.error(exn)
            raise ValidationFailedError(exn)

        return 1

    return 0
