from pathlib import Path

import pytest

from tests.integration import utility_test_functions

workflows_path = Path(__file__).parents[1].joinpath("workflows/")


class TestListOutputs:
    @pytest.mark.parametrize(
        "wdl, json_file, options, output_template",
        [
            (
                "tests/workflows/helloWorld.wdl",
                "tests/workflows/helloWorld.json",
                None,
                [
                    "HelloWorld.output_file: /cromwell-executions/HelloWorld/<workflow-id>/call-HelloWorldTask/execution/stdout",
                    ""
                ],
            ),
            (
                "tests/workflows/helloWorld.wdl",
                "tests/workflows/helloWorld.json",
                ["-d"],
                [
                    "HelloWorld.HelloWorldTask",
                    "\toutput_file: /cromwell-executions/HelloWorld/<workflow-id>/call-HelloWorldTask/execution/stdout",
                    ""
                ],
            ),
            (
                "tests/workflows/helloWorld.wdl",
                "tests/workflows/helloWorld.json",
                ["-j"],
                [
                    "{",
                    '    "HelloWorld.output_file": "/cromwell-executions/HelloWorld/<workflow-id>/call-HelloWorldTask/execution/stdout"',
                    "}",
                    ""
                ],
            ),
            (
                "tests/workflows/helloWorld.wdl",
                "tests/workflows/helloWorld.json",
                ["-j", "-d"],
                [
                    "{",
                    '    "HelloWorld.HelloWorldTask": [',
                    "        {",
                    '            "output_file": "/cromwell-executions/HelloWorld/<workflow-id>/call-HelloWorldTask/execution/stdout"',
                    "        }",
                    "    ]",
                    "}",
                    ""
                ],
            ),
        ],
    )
    def test_list_outputs(
        self,
        local_cromwell_url: str,
        wdl: str,
        json_file: str,
        options: list,
        output_template: list,
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

        # run list-outputs
        status_result = utility_test_functions.run_cromshell_command(
            command=["list-outputs", test_workflow_id],
            exit_code=0,
            options=options,
        )

        status_result_per_line = status_result.stdout.split("\n")

        workflow_outputs = [
            sub.replace('<workflow-id>', test_workflow_id) for sub in output_template
        ]

        print("Print workflow list-outputs results:")
        for line in status_result_per_line:
            print(line)

        assert status_result_per_line == workflow_outputs
