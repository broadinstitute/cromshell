from pathlib import Path

import pytest

from tests.integration import utility_test_functions

workflows_path = Path(__file__).parents[1].joinpath("workflows/")


class TestLogs:
    @pytest.mark.parametrize(
        "wdl, json_file, status, expected_logs, exit_code",
        [
            (
                "tests/workflows/helloWorld.wdl",
                "tests/workflows/helloWorld.json",
                "ALL",
                """HelloWorld.HelloWorldTask:\n\tstatus: Done\n\tstderr: /cromwell-executions/HelloWorld/2686fb3f-d2e6-4a4c-aa66-5dede568310f/call-HelloWorldTask/execution/stderr\n\tstdout: /cromwell-executions/HelloWorld/2686fb3f-d2e6-4a4c-aa66-5dede568310f/call-HelloWorldTask/execution/stdout\n""",
                0,
            ),
            (
                "tests/workflows/helloWorldFail.wdl",
                "tests/workflows/helloWorld.json",
                "Done",
                "No logs found for workflow: 2686fb3f-d2e6-4a4c-aa66-5dede568310f with status: ['Done']",
                1,
            ),
        ],
    )
    def test_logs(
        self,
        local_cromwell_url: str,
        wdl: str,
        json_file: str,
        status: str,
        expected_logs: str,
        exit_code: int,
        ansi_escape,
    ):
        test_workflow_id = utility_test_functions.submit_workflow(
            local_cromwell_url=local_cromwell_url,
            wdl=wdl,
            json_file=json_file,
            exit_code=0,
        )

        utility_test_functions.wait_for_workflow_completion(
            test_workflow_id=test_workflow_id
        )

        # run logs
        logs_result = utility_test_functions.run_cromshell_command(
            command=["logs", "-s", status, test_workflow_id],
            exit_code=exit_code,
        )

        print("Print workflow logs results:")
        print(logs_result.stdout)
        print(logs_result.stderr)
        print(logs_result.exception)

        workflow_logs = (
            ansi_escape.sub("", logs_result.stdout)
            if exit_code == 0
            else str(logs_result.exception)
        )

        id_updated_expected_logs = utility_test_functions.replace_uuids(
            expected_logs, test_workflow_id
        )

        assert workflow_logs == id_updated_expected_logs
