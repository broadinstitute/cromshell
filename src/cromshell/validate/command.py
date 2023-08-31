import logging
from pathlib import Path

import click

import cromshell.utilities.miniwdl_utils as miniwdl
import cromshell.utilities.womtool_utils as womtool

LOGGER = logging.getLogger(__name__)


class ValidationFailedError(Exception):
    pass


class MissingArgumentError(Exception):
    pass


@click.command(name="validate")
@click.argument("wdl", type=click.Path(exists=True), required=True)
@click.argument("wdl_json", type=click.Path(exists=True), required=False)
@click.option(
    "-d",
    "--dependencies-zip",
    required=False,
    type=click.Path(exists=True),
    help="MiniWDL option: ZIP file or directory containing workflow source files "
    "that are used to resolve local imports. This zip bundle will be "
    "unpacked in a sandbox accessible to",
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
    "--no-miniwdl",
    is_flag=True,
    default=False,
    help="Disable miniwdl to validation.",
)
@click.option(
    "--no-womtool",
    is_flag=True,
    default=False,
    help="Disable womtool to validation.",
)
@click.pass_obj
def main(
    config,
    wdl: Path,
    wdl_json: Path,
    dependencies_zip: str,
    strict: bool,
    suppress: tuple,
    no_miniwdl: bool,
    no_womtool: bool,
):
    """
    Validate a WDL workflow and its input JSON using the Cromwell server's womtool API
    and miniwdl.

    Note: Womtool validation via Cromwell server API does not support validation of
    imported files, however miniwdl does.

    """

    LOGGER.info("validate")

    return_code = 0

    if not no_womtool:
        if not wdl_json:
            LOGGER.error("WDL JSON file is required.")
            raise MissingArgumentError("WDL JSON file is required.")

        womtool.womtool_validate_wdl_and_json(
            wdl=str(wdl), wdl_json=str(wdl_json), config=config
        )

    if not no_miniwdl:
        return_code = miniwdl.miniwdl_validate_wdl(
            wdl=wdl, dependencies=dependencies_zip, strict=strict, suppress=suppress
        )

    if return_code == 0:
        print("Validation successful.")
    else:
        print("Validation failed.")

    return return_code
