import json
from datetime import datetime, timedelta, timezone

import pytest
from google.cloud import bigquery

from cromshell.cost import command as cost_command


class TestCost:
    """Test the execution of cost command functions"""

    @pytest.mark.parametrize(
        "detailed, bq_cost_table, query",
        [
            [
                True,
                "cost:table:1",
                """
                SELECT wfid.value as cromwell_workflow_id, service.description, task.value as task_name, sum(cost) as cost
                FROM cost:table:1 as billing, UNNEST(labels) as wfid, UNNEST(labels) as task
                WHERE cost > 0
                AND task.key LIKE "wdl-task-name"
                AND wfid.key LIKE "cromwell-workflow-id"
                AND wfid.value like @workflow_id
                AND partition_time BETWEEN @start_date AND @end_date
                GROUP BY 1,2,3
                ORDER BY 4 DESC
                """,
            ],
            [
                False,
                "cost:table1",
                """
                SELECT sum(cost) as cost
                FROM cost:table1, UNNEST(labels)
                WHERE value LIKE @workflow_id AND partition_time BETWEEN @start_date AND @end_date
                """,
            ],
        ],
    )
    def test_create_bq_query(self, detailed, bq_cost_table, query):
        assert query == cost_command.create_bq_query(
            detailed=detailed, bq_cost_table=bq_cost_table
        )

    def test_create_bq_query_job_config(self):
        workflow_id = "workflowid"
        start_date = "startdate"
        end_date = "enddate"

        assert (
            cost_command.create_bq_query_job_config(
                workflow_id=workflow_id,
                start_date=start_date,
                end_date=end_date,
            ).query_parameters
            == bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter(
                        "workflow_id", "STRING", "%" + workflow_id
                    ),
                    bigquery.ScalarQueryParameter("start_date", "STRING", start_date),
                    bigquery.ScalarQueryParameter("end_date", "STRING", end_date),
                ]
            ).query_parameters
        )

    # def test_check_bq_query_results(self):

    # def test_check_bq_query_for_errors(self):

    @pytest.mark.parametrize(
        "hours_passed, min_hours_needed_to_be_passed, expected_minimum_time_passed",
        [
            [6, 24, False],
            [6, 4, True],
            [36, 24, True],
            [36, 44, False],
        ],
    )
    def test_minimum_time_passed_since_workflow_completion(
        self,
        hours_passed,
        min_hours_needed_to_be_passed,
        expected_minimum_time_passed,
    ):
        end_time = datetime.now(timezone.utc) - timedelta(hours=hours_passed)
        expected_workflow_time_delta = datetime.now(timezone.utc) - end_time

        (
            minimum_time_passed,
            workflow_time_delta,
        ) = cost_command.minimum_time_passed_since_workflow_completion(
            end_time=str(datetime.strftime(end_time, "%Y-%m-%dT%H:%M:%S.%f%z")),
            min_hours=min_hours_needed_to_be_passed,
        )

        assert (minimum_time_passed, workflow_time_delta.seconds) == (
            expected_minimum_time_passed,
            expected_workflow_time_delta.seconds,
        )

    @pytest.mark.parametrize(
        "metadata_name, expected_start_time, expected_end_time",
        [
            [
                "failed_helloworld_metadata.json",
                "2022-03-10T13:24:54.410Z",
                "2022-03-10T13:25:10.367Z",
            ],
            [
                "succeeded_helloworld_metadata.json",
                "2022-10-21T19:09:45.888Z",
                "2022-10-21T19:12:53.940Z",
            ],
            [
                "running_helloworld_metadata.json",
                "2023-02-22T21:33:14.309Z",
                None,
            ],
            [
                "submitted_helloworld_metadata.json",
                None,
                None,
            ],
        ],
    )
    def test_get_submission_start_end_time(
        self, mock_data_path, metadata_name, expected_start_time, expected_end_time
    ):
        with open(mock_data_path.joinpath(metadata_name), "r") as f:
            workflow_metadata = json.load(f)

        (start_time, end_time) = cost_command.get_submission_start_end_time(
            workflow_metadata
        )

        assert (start_time, end_time) == (expected_start_time, expected_end_time)

    # def test_checks_before_query(self):

    @pytest.mark.parametrize(
        "query_rows, cost_header, expected_rounded_rows",
        [
            [
                [{"cost": 0.3215}, {"cost": 0.15615}],
                "cost",
                [{"cost": 0.32}, {"cost": 0.16}],
            ],
            [
                [{"COST": 0.3215}, {"COST": 0.15615}],
                "COST",
                [{"COST": 0.32}, {"COST": 0.16}],
            ],
            [
                [{"COST": 0.3215}, {"COST": 0.15615}],
                "cost",
                [{"COST": 0.3215}, {"COST": 0.15615}],
            ],
        ],
    )
    def test_round_cost_values(
        self, query_rows: list, cost_header: str, expected_rounded_rows: list
    ):
        assert expected_rounded_rows == cost_command.round_cost_values(
            query_rows=query_rows, cost_header=cost_header
        )

    @pytest.mark.parametrize(
        "query_rows, cost_header, expected_rounded_rows",
        [
            [[{"cost": 0.3215}, {"cost": 0.15615}], "cost", 0.48],
            [[{"COST": 0.3215}, {"COST": 0.15615}], "COST", 0.48],
            [[{"COST": 0.3215}, {"COST": 0.15615}], "cost", 0.0],
        ],
    )
    def test_get_query_total_cost(
        self, query_rows: list, cost_header: str, expected_rounded_rows: list
    ):
        assert (
            cost_command.get_query_total_cost(
                query_rows=query_rows, cost_header=cost_header
            )
            == expected_rounded_rows
        )

    @pytest.mark.parametrize(
        "query_rows, cost_header, expected_rows_with_color",
        [
            [
                [{"cost": 0.3215}, {"cost": 0.15615}],
                "cost",
                [{"cost": 0.3215}, {"cost": 0.15615}],
            ],
            [
                [{"COST": 0.3215}, {"COST": 0.15615}],
                "COST",
                [{"COST": 0.3215}, {"COST": 0.15615}],
            ],
            [
                [{"cost": 0.3215}, {"cost": 0.15615}, {"cost": 10.15}],
                "cost",
                [{"cost": 0.3215}, {"cost": 0.15615}, {"cost": "\x1b[91m10.15\x1b[0m"}],
            ],
        ],
    )
    def test_color_cost_outliers(
        self, query_rows: list, cost_header: str, expected_rows_with_color: list
    ):
        assert (
            cost_command.color_cost_outliers(
                detailed_query_rows=query_rows, cost_header=cost_header
            )
            == expected_rows_with_color
        )

    @pytest.mark.parametrize(
        "query_rows, cost_header",
        [
            [
                [{"cost": 0.3215}],
                "cost",
            ],
            [
                [{"COST": 0.3215}, {"COST": 0.15615}],
                "cost",
            ],
        ],
    )
    def test_failure_color_cost_outliers(self, query_rows: list, cost_header: str):
        with pytest.raises(Exception):
            cost_command.color_cost_outliers(
                detailed_query_rows=query_rows, cost_header=cost_header
            )

    # def test_format_bq_query_results():
    @pytest.mark.parametrize(
        "color, query_rows, cost_header, expected_rows_with_color",
        [
            [
                False,
                [{"cost": 0.3215}, {"cost": 0.15615}, {"cost": 10.15}],
                "cost",
                """========
    cost
========
 0.3215
 0.15615
10.15
========
""",
            ],
            [
                True,
                [{"cost": 0.3215}, {"cost": 0.15615}, {"cost": 10.15}],
                "cost",
                """========
    cost
========
 0.3215
 0.15615
\x1b[91m10.15\x1b[0m
========
""",
            ],
        ],
    )
    def test_print_detailed_query_results(
        self,
        color: bool,
        query_rows: list,
        cost_header: str,
        expected_rows_with_color: list,
        capsys,
    ):
        cost_command.print_detailed_query_results(
            color=color, detailed_query_rows=query_rows, cost_header=cost_header
        )
        captured = capsys.readouterr()
        assert captured.out == expected_rows_with_color
