import csv
import logging

import click

from cromshell.utilities import io_utils, workflow_id_utils

LOGGER = logging.getLogger(__name__)


@click.command(name="alias")
@click.argument("workflow_id", required=True)
@click.argument("alias", required=True)
@click.pass_obj
def main(config, workflow_id: str or int, alias: str):
    """
    Label the given workflow ID with the given alias.
    Aliases can be used in place of workflow IDs to reference jobs.

    Remove alias by passing empty double quotes as an alias.
    (e.g. cromshell alias [workflow_id] "")
    """

    LOGGER.info("alias")

    resolved_workflow_id = workflow_id_utils.resolve_workflow_id(
        cromshell_input=workflow_id,
        submission_file_path=config.submission_file_path,
    )

    # Perform Checks
    run_alias_pre_checks(
        alias_name=alias,
        workflow_id=resolved_workflow_id,
        submission_file_path=config.submission_file_path,
    )

    # Set workflow id with given alias
    io_utils.update_all_workflow_database_tsv(
        workflow_database_path=config.submission_file_path,
        workflow_id=resolved_workflow_id,
        column_to_update="ALIAS",
        update_value=alias,
    )

    return 0


def run_alias_pre_checks(
    alias_name: str, workflow_id: str, submission_file_path: str
) -> None:
    """
    Do several checks with input confirm it fine to create the alias
    :param alias_name: Alternate string identifier for workflow submission
    :param workflow_id: Hexadecimal identifier of workflow submission
    :param submission_file_path: Path to cromshell submission file
    :return:
    """

    # check if provided alias contains white spaces or start with a dash
    if not alias_is_valid(alias_name):
        LOGGER.error(
            "Alias %s is invalid, it may not start with a dash or contain whitespace.",
            alias_name,
        )
        raise ValueError(
            f"Alias {alias_name} is invalid, it may not start with a dash or contain "
            f"whitespace. "
        )

    # check if alias already exists
    if alias_exists(alias_name=alias_name, submission_file=submission_file_path):
        LOGGER.error(
            "Can't use '%s' as alias, as it is already being used.", alias_name
        )
        raise ValueError(f"Alias already exists: {alias_name} ")

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
        workflow_id=workflow_id, submission_file=submission_file_path
    )


def alias_is_valid(alias_name: str) -> bool:
    """
    Check if alias name starts with '-' or has a whitespace char
    :param alias_name: Alternate string identifier for workflow submission
    :return:
    """
    if alias_name.startswith("-") or " " in alias_name or alias_name.isdigit():
        return False
    else:
        return True


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


def check_workflow_has_alias(workflow_id: str, submission_file: str) -> None:
    """
    Checks if workflow id has alias listed in submission file, print warning if so.
    :param workflow_id: Hexadecimal identifier of workflow submission
    :param submission_file: Path to cromshell submission file
    :return:
    """

    with open(submission_file, "r") as csv_file:
        reader = csv.DictReader(csv_file, delimiter="\t")
        for row in reader:
            if row["RUN_ID"] == workflow_id:
                if row["ALIAS"] is not None:
                    LOGGER.warning(
                        "Workflow already has alias, its current "
                        "alias '%s' will be replaced",
                        row["ALIAS"],
                    )
