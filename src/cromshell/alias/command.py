import csv
import fileinput
import logging

import click

from cromshell.utilities import workflow_id_utils

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
        cromshell_input=workflow_id
    )

    # Perform Checks
    run_alias_pre_checks(
        alias_name=alias,
        workflow_id=resolved_workflow_id,
        submission_file_path=config.submission_file_path,
    )

    # Set workflow id with given alias
    set_alias_for_workflow_id(
        alias_name=alias,
        workflow_id=resolved_workflow_id,
        submission_file_path=config.submission_file_path,
    )

    return 0


def run_alias_pre_checks(
    alias_name: str, workflow_id: str, submission_file_path: str
) -> None:
    """Do several checks with input confirm it fine to create the alias"""

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
        LOGGER.error("Can't use %s as alias, as it is already being used.", alias_name)
        raise ValueError(f"Alias already exists: {alias_name} ")

    # check if workflow id exists
    if not workflow_id_utils.workflow_id_exists(
        workflow_id=workflow_id, submission_file=submission_file_path
    ):
        LOGGER.error("Could not find workflow id %s in submission file.", workflow_id)
        raise ValueError(
            f"Could not find workflow id {workflow_id} in submission file."
        )


def alias_is_valid(alias_name: str) -> bool:
    """Check if alias name starts with '-' or has a whitespace char"""
    if alias_name.startswith("-") or " " in alias_name:
        return False
    else:
        return True


def alias_exists(alias_name: str, submission_file) -> bool:
    """Check if alias name already exists in submission file"""
    with open(submission_file, "r") as csv_file:
        reader = csv.DictReader(csv_file, delimiter="\t")
        for row in reader:
            if row["ALIAS"] == alias_name:
                return True
        return False


def set_alias_for_workflow_id(
    alias_name: str, workflow_id: str, submission_file_path: str
) -> None:
    """Set the alias name of a workflow id in the submission file"""

    LOGGER.info("Setting workflow %s alias to '%s'", workflow_id, alias_name)

    with fileinput.FileInput(
        submission_file_path, inplace=True, backup=".bak"
    ) as csv_file:
        reader = csv.DictReader(csv_file, delimiter="\t")
        print("\t".join(reader.fieldnames))
        for row in reader:
            if row["RUN_ID"] == workflow_id:
                row["ALIAS"] = alias_name
                print("\t".join(x for x in row.values() if x))
            else:
                print("\t".join(x for x in row.values() if x))
