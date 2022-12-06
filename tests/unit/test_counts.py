import json
import re

import pytest
from cromshell.counts import command as counts_command


class TestCounts:
    """Test the execution status count command functions"""

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

        with open(mock_data_path.joinpath(metadata_name), "r") as f:
            workflow_metadata = json.load(f)

        with open(mock_data_path.joinpath(metadata_summary), "r") as f:
            workflow_summary = f.read()

        counts_command.print_workflow_status(
            workflow_metadata=workflow_metadata, indent="\t"
        )

        captured = capsys.readouterr()

        assert ansi_escape.sub("", captured.out) == workflow_summary

    @pytest.mark.parametrize(
        "metadata_name, call_name, metadata_summary",
        [
            [
                "failed_helloworld_metadata.json",
                "HelloWorld.HelloWorldTask",
                "\tHelloWorld.HelloWorldTask	0 Running, 0 Done, 0 Preempted, 1 Failed",
            ],
            [
                "succeeded_workflow_slim_metadata.json",
                "PBCCSOnlySingleFlowcell.MergeChunks",
                "\tPBCCSOnlySingleFlowcell.MergeChunks	0 Running, 1 Done, 0 Preempted, 0 Failed",
            ],
        ],
    )
    def test_print_call_status(
        self,
        mock_data_path,
        metadata_name,
        call_name,
        metadata_summary,
        ansi_escape,
        capsys,
    ):
        """Note doesn't test for color of print out"""

        with open(mock_data_path.joinpath(metadata_name), "r") as f:
            workflow_metadata = json.load(f)

        counts_command.print_call_status(
            call=call_name,
            indent="\t",
            workflow_calls_metadata=workflow_metadata["calls"],
        )

        captured = capsys.readouterr()
        assert ansi_escape.sub("", captured.out).rstrip() == metadata_summary

    @pytest.mark.parametrize(
        "metadata_name, task_summary",
        [
            [  # metadata test 1
                "failed_helloworld_metadata.json",
                {"HelloWorld.HelloWorldTask": {"Failed": 1}},
            ],
            [  # metadata test 2
                "succeeded_workflow_slim_metadata.json",
                {
                    "PBCCSOnlySingleFlowcell.FinalizeCCSMetrics": {"Done": 1},
                    "PBCCSOnlySingleFlowcell.FinalizeMergedRuns": {"Done": 1},
                    "PBCCSOnlySingleFlowcell.FindBams": {"Done": 1},
                    "PBCCSOnlySingleFlowcell.GetRunInfo": {"Done": 1},
                    "PBCCSOnlySingleFlowcell.MergeCCSReports": {"Done": 1},
                    "PBCCSOnlySingleFlowcell.MergeChunks": {"Done": 1},
                    "PBCCSOnlySingleFlowcell.ShardLongReads": {"Done": 1},
                    "ScatterAt51_18": {"Done": 1},
                },
            ],
        ],
    )
    def test_print_task_status_summary(
        self, mock_data_path, metadata_name, task_summary, capsys
    ):

        with open(mock_data_path.joinpath(metadata_name), "r") as f:
            workflow_metadata = json.load(f)

        counts_command.print_task_status_summary(workflow_metadata=workflow_metadata)
        captured = capsys.readouterr()
        assert captured.out.rstrip() == json.dumps(
            task_summary, indent=4, sort_keys=True
        )

    @pytest.mark.parametrize(
        "test_shards, shard_count",
        # The test_shards is a very minimal representation of a task call for a
        # workflow metadata. Normally the list contains several other pieces of call
        # info but for this test the focus is on executionStatus and shardIndex
        [
            [
                # test_shard 1: having one failed shard
                [{"executionStatus": "Failed", "shardIndex": -1}],
                # failed_shards
                {"Failed": 1},
            ],
            [
                # test_shard 2: having more than one shard and different statuses
                [
                    {"executionStatus": "Done", "shardIndex": 0},
                    {"executionStatus": "Failed", "shardIndex": 1},
                    {"executionStatus": "Done", "shardIndex": 2},
                    {"executionStatus": "Failed", "shardIndex": 3},
                ],
                # failed_shards
                {"Done": 2, "Failed": 2},
            ],
        ],
    )
    def test_get_shard_status_count(self, test_shards, shard_count):
        assert (
            counts_command.get_shard_status_count(
                shards=test_shards,
            )
            == shard_count
        )

    @pytest.mark.parametrize(
        "test_shards, failed_index",
        [
            [
                # test_shard 1: having one failed shard
                [{"executionStatus": "Failed", "shardIndex": -1}],
                # failed_shards
                [-1],
            ],
            [
                # test_shard 2: having more than one shard and different statuses
                [
                    {"executionStatus": "Done", "shardIndex": 0},
                    {"executionStatus": "Failed", "shardIndex": 1},
                    {"executionStatus": "Done", "shardIndex": 2},
                    {"executionStatus": "Failed", "shardIndex": 3},
                ],
                # failed_shards
                [1, 3],
            ],
            [
                # test_shard 1: having no failed shard
                [{"executionStatus": "Done", "shardIndex": -1}],
                # failed_shards
                [],
            ],
        ],
    )
    def test_get_list_of_failed_shards(self, test_shards, failed_index):
        assert (
            counts_command.get_list_of_failed_shards(
                shards=test_shards,
            )
            == failed_index
        )

    @pytest.mark.parametrize(
        "test_shards, grouped_shards",
        [
            [
                # test_shard 1: having one shard
                [{"executionStatus": "Done", "shardIndex": -1}],
                # grouped_shard 1
                {"Done": [{"executionStatus": "Done", "shardIndex": -1}]},
            ],
            [
                # test_shard 2: having more than one shard and different statuses
                [
                    {"executionStatus": "Done", "shardIndex": 0},
                    {"executionStatus": "Failed", "shardIndex": 1},
                    {"executionStatus": "Done", "shardIndex": 2},
                    {"executionStatus": "Failed", "shardIndex": 3},
                ],
                # grouped_shard 2
                {
                    "Done": [
                        {"executionStatus": "Done", "shardIndex": 0},
                        {"executionStatus": "Done", "shardIndex": 2},
                    ],
                    "Failed": [
                        {"executionStatus": "Failed", "shardIndex": 1},
                        {"executionStatus": "Failed", "shardIndex": 3},
                    ],
                },
            ],
        ],
    )
    def test_group_shards_by_status(self, test_shards, grouped_shards):
        assert counts_command.group_shards_by_status(test_shards) == grouped_shards

    @pytest.mark.parametrize(
        "shard_status_count",
        [
            {"Done": 6, "Failed": 20, "FakeStatus1": 36},
            {"Done": 6, "Failed": 20, "FakeStatus1": 36, "FakeStatus2": 36},
        ],
    )
    def test_get_unknown_status(self, shard_status_count):

        known_statuses: list = ["Done", "Failed", "RetryableFailure", "Running"]
        unknown_shard_status: list = []
        shards_unknown: int = 0

        for status in shard_status_count:
            if status not in known_statuses:
                shards_unknown = shards_unknown + shard_status_count[status]
                unknown_shard_status.append(status)

        assert counts_command.get_unknown_status(
            shard_status_count=shard_status_count, known_statuses=known_statuses
        ) == (shards_unknown, unknown_shard_status)


# Remove the ANSI escape sequences from a string
# https://stackoverflow.com/questions/14693701
@pytest.fixture
def ansi_escape():
    return re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
