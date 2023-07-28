import logging
from pathlib import Path

import click
from WDL import CLI as miniwdlCLI
from WDL import Error as miniwdlError

import cromshell.utilities.womtool_utils as womtool

LOGGER = logging.getLogger(__name__)


class ValidationFailedError(Exception):
    pass


class MissingArgument(Exception):
    pass


@click.command(name="validate")
@click.argument("wdl", type=click.Path(exists=True), required=True)
@click.argument("wdl_json", type=click.Path(exists=True), required=False)
@click.option(
    "-d",
    "--dependencies",
    required=False,
    multiple=True,
    type=click.Path(exists=True),
    help="MiniWDL option: Directory containing workflow source files that are "
    "used to resolve local imports. (can supply multiple times)",
)
@click.option(
    "-s",
    "--strict",
    is_flag=True,
    default=False,
    help="MiniWDL option: Exit with nonzero status code if any lint warnings are shown "
    "(in addition to syntax and type errors)",
)
@click.option(
    "-sup",
    "--suppress",
    required=False,
    multiple=True,
    help="MiniWDL option: Warnings to disable e.g. StringCoercion,NonemptyCoercion. (can supply multiple times)",
)
@click.option(
    "--miniwdl",
    is_flag=True,
    default=False,
    help="Use miniwdl to validate WDL file. This supports dependencies validation,"
    "but ignores input JSON file)",
)
@click.pass_obj
def main(
    config,
    wdl: Path,
    wdl_json: Path,
    dependencies: tuple,
    strict: bool,
    suppress: tuple,
    miniwdl: bool,
):
    """
    Validate a WDL workflow and its input JSON using the Cromwell server's womtool API
    by default and has the option to use miniwdl as an alternative.
    """

    LOGGER.info("validate")

    return_code = 0

    if miniwdl:
        return_code = miniwdl_validate_wdl(
            wdl=wdl, dependencies=dependencies, strict=strict, suppress=suppress
        )
    else:
        if not wdl_json:
            LOGGER.error("WDL JSON file is required.")
            raise MissingArgument("WDL JSON file is required.")

        womtool.womtool_validate_wdl_and_json(
            wdl=str(wdl), wdl_json=str(wdl_json), config=config
        )

    if return_code == 0:
        print("Validation successful.")
    else:
        print("Validation failed.")

    return return_code


def miniwdl_validate_wdl(
    wdl: Path, dependencies: tuple, strict: bool, suppress: []
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
        miniwdlCLI.print_error(exn)

        if logging.getLogger().level == logging.DEBUG:
            LOGGER.error(exn)
            raise ValidationFailedError(exn)

        return 1

    return 0
