import json
from importlib import reload
from pathlib import Path
from traceback import print_exception

from click.testing import CliRunner

import cromshell.utilities.workflow_status_utils as wsu
from cromshell.__main__ import main_entry as cromshell
from cromshell.utilities import cromshellconfig


def run_cromshell_command(
    command: list, exit_code: int, subcommand_options: list = None
):
    """
    Run cromshell alias using CliRunner and assert job is successful

    :param subcommand_options: The options to pass to the subcommand
    :param command: The subcommand, options, and arguments in list form e.g.
    [
        "alias",
        "--",
        workflow_id,
        alias_name,
    ]
    :param exit_code: The expected exit code
    :return: results from execution
    """

    if subcommand_options:
        command_with_options = command[:1] + subcommand_options + command[1:]
    else:
        command_with_options = command

    runner = CliRunner(mix_stderr=False)
    # The absolute path will be passed to the invoke command because
    # the test is being run in temp directory created by CliRunner.
    with runner.isolated_filesystem():
        result = runner.invoke(cromshell, command_with_options)
        assert result.exit_code == exit_code, (
            f"\nCOMMAND:\n{command_with_options}"
            f"\nSTDOUT:\n{result.stdout}"
            f"\nSTDERR:\n{result.stderr}"
            f"\nExceptions:\n{result.exception}"
            f"\n{print_exception(*result.exc_info)}"
        )
        return result


def wait_for_workflow_completion(
    test_workflow_id: str, status_to_reach: str or list = None
):
    """

    :param test_workflow_id: The workflow id whose status will be checked
    :param status_to_reach: The status to wait for. By default, will be Succeeded
    or Failed.
    :return:
    """

    if status_to_reach is None:
        status_to_reach = (
            wsu.WorkflowStatuses.SUCCEEDED.value + wsu.WorkflowStatuses.FAILED.value
        )

    import time

    count = 0
    status = ""
    print("Printing workflow status:")
    while count < 10:
        time.sleep(5)
        count += 1
        # run status check every 5 sec until done, max 10x
        status_result = run_cromshell_command(
            command=["status", test_workflow_id],
            exit_code=0,
        )
        print(status_result.stdout)
        status_result_formatted = json.loads(status_result.stdout)
        status = status_result_formatted["status"]

        if status in status_to_reach:
            break

    assert status in status_to_reach, f"Workflow didn't reach status: {status_to_reach}"


def submit_workflow(
    local_cromwell_url: str,
    wdl: str,
    json_file: str,
    exit_code: int,
) -> str:
    # Run cromshell submit
    submit_result = run_cromshell_submit(
        wdl=wdl,
        json_file=json_file,
        no_validation=False,
        exit_code=exit_code,
        local_cromwell_url=local_cromwell_url,
    )

    stdout_substring_formatted = json.loads(submit_result.stdout)
    return stdout_substring_formatted["id"]


def run_cromshell_submit(
    wdl: str,
    json_file: str,
    no_validation: bool,
    local_cromwell_url: str,
    exit_code: int,
):
    """Run cromshell submit using CliRunner and assert job is successful"""

    reload(cromshellconfig)
    runner = CliRunner(mix_stderr=False)
    # The absolute path will be passed to the invoke command because
    # the test is being run in temp directory created by CliRunner.
    absolute_wdl = str(Path(wdl).resolve())
    absolute_json = str(Path(json_file).resolve())
    optional_args = []
    if no_validation:
        optional_args.append("--no-validation")
    with runner.isolated_filesystem():
        result = runner.invoke(
            cromshell,
            [
                "--cromwell_url",
                local_cromwell_url,
                "--no_turtle",
                "submit",
                absolute_wdl,
                absolute_json,
            ]
            + optional_args,
        )
        assert result.exit_code == exit_code, (
            f"\nSTDOUT:\n{result.stdout}"
            f"\nSTDERR:\n{result.stderr}"
            f"\nExceptions:\n{result.exception}"
            f"\n{print_exception(*result.exc_info)}"
        )
        return result


import re
def replace_uuids(input_string: str, replacement_uuid: str):
    """
    Replace all UUIDs in a string with a given UUID
    :param input_string: the string to replace UUIDs in
    :param replacement_uuid: the UUID to replace all UUIDs in the string with
    :return:
    """
    # Define the pattern to match 128-bit UUIDs
    uuid_pattern = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"

    # Generate the replacement UUID
    new_uuid = str(replacement_uuid)

    # Use regular expressions to find and replace UUIDs in the string
    output_string = re.sub(uuid_pattern, new_uuid, input_string)

    return output_string
