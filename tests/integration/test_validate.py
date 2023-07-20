from tests.integration import utility_test_functions
import pytest
from pathlib import Path

class TestValidate:
    """Test the version command."""

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
    def test_validate(self, wdl, results, workflows_path):
        workflow_path = str(Path.joinpath(workflows_path, wdl))
        validate_result = utility_test_functions.run_cromshell_command(
            command=["validate", workflow_path, "--suppress", "UnusedDeclaration", "--suppress", "MixedIndentation"],
            exit_code=0,
        )

        print("Print version results:")
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
    def test_validate_suppress(self, wdl, suppress, workflows_path):
        workflow_path = str(Path.joinpath(workflows_path, wdl))
        validate_result = utility_test_functions.run_cromshell_command(
            command=["validate", workflow_path, "--suppress", suppress],
            exit_code=0,
        )

        print("Print version results:")
        print(validate_result.stdout)
        if suppress:
            assert suppress not in validate_result.stdout
        else:
            assert suppress in validate_result.stdout
