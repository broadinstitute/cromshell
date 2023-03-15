import json
import re

import pytest

from cromshell.list_outputs import command as list_outputs_command


class TestListOutputs:
    """Test the execution list-outputs command functions"""

    @pytest.mark.parametrize(
        "metadata_name, metadata_summary",
        [
            [
                "failed_helloworld_metadata.json",
                "counts/test_workflow_status_failed_helloword_metadata.txt",
            ],
            [
                "succeeded_workflow_slim_metadata.json",
                "counts/test_workflow_status_succeded_workflow_slim_metadata.txt",
            ],
        ],
    )
    def test_workflow_status(
        self, mock_data_path, metadata_name, metadata_summary, ansi_escape, capsys
    ):
        """Note doesn't test for color of print out"""


# def get_workflow_level_outputs(config) -> dict:


# def test_get_task_level_outputs(config) -> dict:

    @pytest.mark.parametrize(
        "workflow_metadata, outputs_metadata",
        [
            [
                "succeeded_helloworld.metadata.json",
                "list_outputs/succeeded_helloworld.outputs.metadata.json",
            ],
        ],
    )
    def test_filer_outputs_from_workflow_metadata(
        self, mock_data_path, tests_metadata_path, workflow_metadata, outputs_metadata, capsys
    ):
        with open(tests_metadata_path.joinpath(workflow_metadata), "r") as f:
            workflow_metadata = json.load(f)

        with open(mock_data_path.joinpath(outputs_metadata), "r") as f:
            outputs_metadata = f.read()
        print("\n")
        print(list_outputs_command.filer_outputs_from_workflow_metadata(workflow_metadata))

        assert list_outputs_command.filer_outputs_from_workflow_metadata(workflow_metadata) == outputs_metadata


#
#
# def print_task_level_outputs(output_metadata: dict) -> None:
#
#
# def print_output_metadata(outputs_metadata: dict, indent: bool) -> None:
#
#
# def print_output_name_and_file(
#         task_output_name: str, task_output_value: str, indent: bool = True
# ) -> None:
#
# def is_path_or_url_like(in_string: str) -> bool:
