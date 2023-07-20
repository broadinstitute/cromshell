import logging
from pathlib import Path

import click
from WDL import CLI as miniwdlCLI
from WDL import Error as miniwdlError

LOGGER = logging.getLogger(__name__)

class ValidationFailedError(Exception):
    pass

@click.command(name="validate")
@click.argument("wdl", type=click.Path(exists=True), required=True)
@click.option(
    "-d",
    "--dependencies",
    required=False,
    multiple=True,
    type=click.Path(exists=True),
    help="Directory containing workflow source files that are "
    "used to resolve local imports. (can supply multiple times)",
)
@click.option(
    "-s",
    "--strict",
    is_flag=True,
    default=False,
    help="Exit with nonzero status code if any lint warnings are shown "
         "(in addition to syntax and type errors)"
)
@click.option(
    "-sup",
    "--suppress",
    required=False,
    multiple=True,
    help="Warnings to disable e.g. StringCoercion,NonemptyCoercion. (can supply multiple times)",
)
@click.pass_obj
def main(config, wdl: Path, dependencies: tuple, strict: bool, suppress: tuple):
    """
    Validate a WDL workflow using miniwdl.
    """

    LOGGER.info("validate")

    return_code = 0

    # Check dependencies path exists:
    for dep in dependencies:
        Path(dep).resolve(strict=True)

    # Validate the WDL file:
    try:
        miniwdlCLI.check(
            uri=[str(wdl)],
            path=list(dependencies),
            strict=strict,
            suppress=",".join([str(item) for item in suppress]) # Turn into string
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

        return_code = 1

    if return_code == 0:
        print("Validation successful.")
    else:
        print("Validation failed.")

    return return_code
