import pytest

from cromshell.utilities.cromshellconfig import WorkflowStatuses
from tests.integration import utility_test_functions


class TestAbort:
    @pytest.mark.parametrize(
        "wdl, json_file",
        [
            (
                "tests/workflows/helloWorld.wdl",
                "tests/workflows/helloWorld.json",
            )
        ],
    )
    def test_logs(
        self,
        local_cromwell_url: str,
        wdl: str,
        json_file: str,
    ):
        test_workflow_id = utility_test_functions.submit_workflow(
            local_cromwell_url=local_cromwell_url,
            wdl=wdl,
            json_file=json_file,
            exit_code=0,
        )

        abort_result = utility_test_functions.run_cromshell_command(
            command=["abort", test_workflow_id],
            exit_code=0,
        )

        print("Print workflow counts results:")
        print(abort_result.stdout)

        utility_test_functions.wait_for_workflow_completion(
            test_workflow_id=test_workflow_id,
            status_to_reach=WorkflowStatuses.ABORTED.value,
        )
