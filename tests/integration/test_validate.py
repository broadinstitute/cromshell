from pathlib import Path

import pytest

from tests.integration import utility_test_functions


class TestValidate:
    """Test the version command."""

    @pytest.mark.parametrize(
        "wdl, wdl_json, exit_code, expected_results",
        [
            (
                "helloWorld.wdl",
                "",
                2,
                "",
            ),
            (
                "helloWorld.wdl",
                "helloWorld.json",
                0,
                "Validation successful.\n",
            ),
            (
                "not_valid.wdl",
                "not_valid.json",
                1,
                "",
            ),
        ],
    )
    def test_validate(
        self,
        wdl,
        wdl_json,
        exit_code,
        expected_results,
        workflows_path,
        local_cromwell_url: str,
    ):
        workflow_path = str(Path.joinpath(workflows_path, wdl))
        wdl_json_path = str(Path.joinpath(workflows_path, wdl_json)) if wdl_json else ""
        validate_result = utility_test_functions.run_cromshell_command(
            command=[
                "--no_turtle",
                "--cromwell_url",
                local_cromwell_url,
                "validate",
                workflow_path,
                wdl_json_path,
            ],
            exit_code=exit_code,
        )

        print("Print version results:")
        print(validate_result.stdout)

        if expected_results:
            assert expected_results in str(validate_result.stdout)

    @pytest.mark.parametrize(
        "wdl, results",
        [
            (
                "helloWorld.wdl",
                "Validation successful.\n",
            ),
            (
                "not_valid.wdl",
                "Validation failed.\n",
            ),
        ],
    )
    def test_validate_using_miniwdl(self, wdl, results, workflows_path):
        workflow_path = str(Path.joinpath(workflows_path, wdl))
        validate_result = utility_test_functions.run_cromshell_command(
            command=[
                "validate",
                workflow_path,
                "--no-womtool",
            ],
            exit_code=0,
        )

        print("Print validate results:")
        print(validate_result.stdout)

        assert results in validate_result.stdout

    @pytest.mark.parametrize(
        "wdl, suppress",
        [
            (
                "helloWorld.wdl",
                "UnusedDeclaration",
            ),
            (
                "helloWorld.wdl",
                "",
            ),
        ],
    )
    def test_validate_suppress_using_miniwdl(self, wdl, suppress, workflows_path):
        workflow_path = str(Path.joinpath(workflows_path, wdl))
        validate_result = utility_test_functions.run_cromshell_command(
            command=["validate", workflow_path, "--suppress", suppress, "--no-womtool"],
            exit_code=0,
        )

        print("Print version results:")
        print(validate_result.stdout)
        if suppress:
            assert suppress not in validate_result.stdout
        else:
            assert suppress in validate_result.stdout
