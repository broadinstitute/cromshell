import io
import logging
from contextlib import redirect_stdout
from pathlib import Path

from cromshell import log
from cromshell.utilities.io_utils import dead_turtle

LOGGER = logging.getLogger(__name__)


class ValidationFailedError(Exception):
    pass


def miniwdl_validate_wdl(
    wdl: Path,
    dependencies: tuple = (),
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

    for dep in dependencies:
        Path(dep).resolve(strict=True)

    try:
        f = io.StringIO()
        with redirect_stdout(f):
            # Importing miniwdl.check here to help with stdout redirection
            from WDL.CLI import check as miniwdl_check

            miniwdl_check(
                uri=[str(wdl)],
                path=list(dependencies),
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
