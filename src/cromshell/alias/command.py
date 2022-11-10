import csv
import logging
import re

import click

import cromshell.utilities.submissions_file_utils as submissions_file_utils
import cromshell.utilities.workflow_id_utils as workflow_id_utils

LOGGER = logging.getLogger(__name__)


@click.command(name="alias")
@click.argument("workflow_id", required=True)
@click.argument("alias", required=True)
@click.pass_obj
def main(config, workflow_id: str or int, alias: str):
    """
    Label the given workflow ID or relative id with the given alias.
    Aliases can be used in place of workflow IDs to reference jobs.

    Alias must NOT start with '-', have a whitespace char, or be a digit.

    Remove alias by passing empty double quotes as an alias.
    (e.g. cromshell alias [workflow_id] "")

    """

    LOGGER.info("alias")

    run_alias_pre_checks(
        alias_name=alias,
        submission_file_path=config.submission_file_path,
    )

    resolved_workflow_id = workflow_id_utils.resolve_workflow_id(
        cromshell_input=workflow_id,
        submission_file_path=config.submission_file_path,
    )

    run_workflow_checks(
        workflow_id=resolved_workflow_id,
        submission_file_path=config.submission_file_path,
        alias_name=alias,
    )

    submissions_file_utils.update_row_values_in_submission_db(
        workflow_database_path=config.submission_file_path,
        workflow_id=resolved_workflow_id,
        column_to_update=submissions_file_utils.MutableSubmissionFileHeader.Alias.value,
        update_value=alias,
    )

    return 0


def run_alias_pre_checks(alias_name: str, submission_file_path: str) -> None:
    """
    Do several checks with input confirm it fine to create the alias
    :param alias_name: Alternate string identifier for workflow submission
    :param submission_file_path: Path to cromshell submission file
    :return:
    """

    # check if provided alias contains white spaces or start with a dash
    if alias_is_invalid(alias_name):
        message = (
            f"Alias {alias_name} is invalid, it may not start with a dash, "
            f"contain whitespace, or be a digit. "
        )
        LOGGER.error(message)
        raise ValueError(message)

    # check if alias already exists
    if alias_exists(alias_name=alias_name, submission_file=submission_file_path):
        LOGGER.error(
            "Can't use '%s' as alias, as it is already being used.", alias_name
        )
        raise ValueError(f"Alias already exists: {alias_name} ")


def run_workflow_checks(
    workflow_id: str, submission_file_path: str, alias_name: str
) -> None:
    """
    Run checks on workflow id to confirm it exists and whether it already has an alias
    :param workflow_id: Hexadecimal identifier of workflow submission
    :param submission_file_path: Path to cromshell submission file
    :return:
    """
    # check if workflow id exists
    if not workflow_id_utils.workflow_id_exists(
        workflow_id=workflow_id, submission_file=submission_file_path
    ):
        LOGGER.error("Could not find workflow id %s in submission file.", workflow_id)
        raise ValueError(
            f"Could not find workflow id {workflow_id} in submission file."
        )

    # check if workflow id already has alias, if so print a warning message
    check_workflow_has_alias(
        workflow_id=workflow_id,
        submission_file=submission_file_path,
        alias_name=alias_name,
    )


def alias_is_invalid(alias_name: str) -> bool:
    """
    Check if alias name starts with '-' or has a whitespace char or is a digit
    :param alias_name: Alternate string identifier for workflow submission
    :return:
    """
    return (
        True
        if (
            alias_name.startswith("-")
            or bool(re.search(r"\s+", alias_name))
            or alias_name.isdigit()
        )
        else False
    )


def alias_exists(alias_name: str, submission_file) -> bool:
    """
    Check if alias name already exists in submission file
    :param alias_name: Alternate string identifier for workflow submission
    :param submission_file: Path to cromshell submission file
    :return:
    """
    with open(submission_file, "r") as csv_file:
        reader = csv.DictReader(csv_file, delimiter="\t")
        for row in reader:
            if (row["ALIAS"] == alias_name) and (row["ALIAS"] != ""):
                return True
        return False


def check_workflow_has_alias(
    workflow_id: str, submission_file: str, alias_name: str
) -> None:
    """
    Checks if workflow id has alias listed in submission file, print warning if so
    :param workflow_id: Hexadecimal identifier of workflow submission
    :param submission_file: Path to cromshell submission file
    :param alias_name: the new alias name
    :return:
    """

    with open(submission_file, "r") as csv_file:
        reader = csv.DictReader(csv_file, delimiter="\t")
        for row in reader:
            if row["RUN_ID"] == workflow_id:
                if row["ALIAS"] != "":
                    if alias_name == "":
                        LOGGER.warning(
                            "Workflows current alias '%s' will be removed.",
                            row["ALIAS"],
                        )
                    else:
                        LOGGER.warning(
                            "Workflows current alias '%s' will be replaced with '%s'.",
                            row["ALIAS"],
                            alias_name,
                        )
