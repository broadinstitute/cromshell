import json
from pathlib import Path

import pytest

from tests.integration import test_submit, utility_test_functions

workflows_path = Path(__file__).parents[1].joinpath("workflows/")


def wait_for_workflow_completion(test_workflow_id: str):
    import time

    count = 0
    status = ""
    print("Printing workflow status:")
    while count < 10:
        time.sleep(5)
        count += 1
        # run status check every 5 sec until done, max 10x
        status_result = utility_test_functions.run_cromshell_command(
            command=["status", test_workflow_id],
            exit_code=0,
        )
        print(status_result.stdout)
        status_result_formatted = json.loads(status_result.stdout)
        status = status_result_formatted["status"]
        print(status)
        if status == "Failed" or status == "Succeeded":
            break

    assert status == "Failed" or "Succeeded", "Workflow did not complete"


def submit_workflow(
    local_cromwell_url: str,
    wdl: str,
    json_file: str,
    exit_code: int,
) -> str:
    # Run cromshell submit
    submit_result = test_submit.run_cromshell_submit(
        wdl=wdl,
        json_file=json_file,
        no_validation=False,
        exit_code=exit_code,
        local_cromwell_url=local_cromwell_url,
    )

    stdout_substring_formatted = json.loads(submit_result.stdout)
    return stdout_substring_formatted["id"]


class TestCounts:
    @pytest.mark.parametrize(
        "wdl, json_file, should_fail, call_summary, workflow_state",
        [
            (
                "tests/workflows/helloWorld.wdl",
                "tests/workflows/helloWorld.json",
                False,
                "\tHelloWorld.HelloWorldTask\t0 Running, 1 Done, 0 Preempted, 0 Failed",
                "Succeeded",
            ),
            (
                "tests/workflows/helloWorldFail.wdl",
                "tests/workflows/helloWorld.json",
                True,
                "\tHelloWorld.HelloWorldTask\t0 Running, 0 Done, 0 Preempted, 1 Failed",
                "Failed",
            ),
        ],
    )
    def test_counts(
        self,
        local_cromwell_url: str,
        wdl: str,
        json_file: str,
        should_fail: bool,
        call_summary: str,
        workflow_state: str,
        ansi_escape,
    ):
        # submit workflow
        test_workflow_id = submit_workflow(
            local_cromwell_url=local_cromwell_url,
            wdl=wdl,
            json_file=json_file,
            exit_code=0,
        )

        wait_for_workflow_completion(test_workflow_id=test_workflow_id)

        # run counts
        status_result = utility_test_functions.run_cromshell_command(
            command=["counts", test_workflow_id],
            exit_code=0,
        )

        status_result_per_line = status_result.stdout.split("\n")

        print("Print workflow counts results:")
        print(status_result_per_line[0])
        print(status_result_per_line[1])

        # The workflows being used here will only generate 2 lines from the counts
        # command, but if testing more complicated workflows the second_line will
        # need to be asserted in a different manner to include all the calls within
        # the workflow being tested.
        first_line = ansi_escape.sub("", status_result_per_line[0])
        second_line = ansi_escape.sub("", status_result_per_line[1])

        assert first_line == test_workflow_id + "\t" + workflow_state
        assert second_line == call_summary