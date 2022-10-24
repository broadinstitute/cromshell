from pathlib import Path

import pytest

from tests.integration import utility_test_functions

workflows_path = Path(__file__).parents[1].joinpath("workflows/")


class TestLogs:
    @pytest.mark.parametrize(
        "wdl, json_file, expected_logs",
        [
            (
                "tests/workflows/helloWorld.wdl",
                "tests/workflows/helloWorld.json",
                "No logs with status ['Failed'] found for workflow, try adding the argument '-s ALL' to list logs with any status\n",
            ),
            (
                "tests/workflows/helloWorldFail.wdl",
                "tests/workflows/helloWorld.json",
                "HelloWorld.HelloWorldTask:\tFailed\t Backend Logs Not Found\n",
            ),
        ],
    )
    def test_logs(
        self,
        local_cromwell_url: str,
        wdl: str,
        json_file: str,
        expected_logs: str,
        ansi_escape,
    ):
        # submit workflow
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
            command=["logs", test_workflow_id],
            exit_code=0,
        )

        print("Print workflow counts results:")
        print(logs_result.stdout)

        workflow_logs = ansi_escape.sub("", logs_result.stdout)

        assert workflow_logs == expected_logs
