import pytest
from pathlib import Path
import json

from cromshell.execution_status_count import command as execution_status_count_command


class TestAlias:
    """Test the execution status count command functions"""

    #def test_pretty_execution_status

    #def test_print_workflow_status(self) -> None:

    # print_task_status
    # print_task_status_summary
    # get_shard_status_count

    def test_print_list_of_failed_shards(self, mock_data_path):
        workflow_metadata_file = mock_data_path.joinpath("failed_helloworld_metadata.txt")
        with open(workflow_metadata_file, "r") as ff:
            workflow_metadata = json.load(ff)

        task = list(workflow_metadata["calls"].keys())[0]
        shards = workflow_metadata["calls"][task]

        indent = "\t"
        assert (
            execution_status_count_command.print_list_of_failed_shards(
                shards=shards, indent=indent, task_status_font="red"
            ) == "\tFailed shards: [-1]"
        )
