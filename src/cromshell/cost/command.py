import logging
import statistics
from datetime import datetime, timezone, timedelta

import click
from google.cloud import bigquery
from tabulate import tabulate

import cromshell.utilities.command_setup_utils as command_setup_utils
import cromshell.utilities.config_options_file_utils as cofu
import cromshell.utilities.workflow_id_utils as workflow_id_utils
import cromshell.metadata.command as metadata


LOGGER = logging.getLogger(__name__)


@click.command(name="cost")
@click.argument("workflow_id", required=True)
@click.option(
    "-c",
    "--color",
    is_flag=True,
    default=False,
    help="Color cost outliers.",
)
@click.option(
    "-d",
    "--detailed",
    is_flag=True,
    default=False,
    help="Get the cost for a workflow at the task level",
)
@click.pass_obj
def main(config, workflow_id: str or int, detailed: bool, color: bool):
    """
    Get the cost for a workflow.
    Only works for workflows that completed more than 24 hours ago on GCS.
    Requires the 'bq_cost_table' key in the cromshell configuration file to be
    set to the big query cost table for your organization.
    """

    LOGGER.info("cost")

    resolved_workflow_id = command_setup_utils.resolve_workflow_id_and_server(
        workflow_id=workflow_id,
        cromshell_config=config,
    )

    workflow_id_utils.check_workflow_id_in_submission_file(
        workflow_id=resolved_workflow_id, submission_file=config.submission_file_path
    )

    cofu.check_key_is_configured(
        key_to_check="bq_cost_table",
        config_options=config.cromshell_config_options,
        config_file_path=config.cromshell_config_path
    )
    LOGGER.info("Using cost table: %s", config.cromshell_config_options["bq_cost_table"])

    # Get time workflow finished using metadata command (error if not finished)
    LOGGER.info("Retrieving workflow metadata")
    workflow_metadata = metadata.format_metadata_params_and_get_metadata(
        config=config,
        exclude_keys=False,
        metadata_param=["start", "status", "id", "end", "workflowProcessingEvents"]
    )
    start_time, end_time = get_submission_start_end_time(workflow_metadata)

    LOGGER.info("Checking workflow completed and finished past 24hrs")
    checks_before_query(
        start_time=start_time,
        end_time=end_time,
        workflow_id=resolved_workflow_id
    )

    LOGGER.info("Querying BQ")
    # Create start and end time for query, plus/minus a day from start and finish
    query_start_time = str(
        datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S.%f%z") - timedelta(days=1))
    query_end_time = str(
        datetime.strptime(end_time, "%Y-%m-%dT%H:%M:%S.%f%z") + timedelta(days=1))

    query_results = query_bigquery(
        workflow_id=resolved_workflow_id,
        bq_database=config.cromshell_config_options["bq_cost_table"],
        start_date=query_start_time,
        end_date=query_end_time,
        detailed=detailed
    )

    query_rows: list[dict] = [dict(row) for row in query_results]
    query_rows_cost_rounded: list[dict] = round_cost_values(query_rows)

    if detailed and color:
        print(
            tabulate(
                color_cost_outliers(query_rows_cost_rounded=query_rows_cost_rounded),
                headers="keys"
            )
        )
    else:
        print(tabulate(query_rows_cost_rounded, headers="keys"))

    print("Costs rounded to nearest cent.")


def query_bigquery(
    workflow_id: str,
    bq_database: str,
    start_date: str,
    end_date: str,
    detailed: bool
):
    """
    Query BigQuery for workflow cost.

    :param detailed: Whether to query cost sum or cost per task
    :param workflow_id:
    :param bq_database: The bq database table name being queried for workflow cost.
    :param start_date: Date workflow started
    :param end_date: Date workflow finished
    :return:
    """

    client = bigquery.Client()

    if detailed:
        query = f"""
                SELECT wfid.value as cromwell_workflow_id, service.description, task.value as task_name, sum(cost) as cost
                FROM {bq_database} as billing, UNNEST(labels) as wfid, UNNEST(labels) as task
                WHERE cost > 0
                AND task.key LIKE "wdl-task-name"
                AND wfid.key LIKE "cromwell-workflow-id"
                AND wfid.value like @workflow_id
                AND partition_time BETWEEN @start_date AND @end_date
                GROUP BY 1,2,3
                ORDER BY 4 DESC
            """
    else:
        query = f"""
                SELECT sum(cost) as cost
                FROM {bq_database}, UNNEST(labels)
                WHERE value LIKE @workflow_id AND partition_time BETWEEN @start_date AND @end_date
            """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("workflow_id", "STRING", "%" + workflow_id),
            bigquery.ScalarQueryParameter("start_date", "STRING", start_date),
            bigquery.ScalarQueryParameter("end_date", "STRING", end_date),
        ]
    )
    query_job = client.query(query, job_config=job_config)

    if query_job.errors:
        LOGGER.error(f"Somthing went wrong with query. Message: {query_job.errors}")
        raise Exception(f"Somthing went wrong with query. Message: {query_job.errors}")

    query_results = query_job.result()

    # First condition applies to a 'detailed' query to confirm results were obtained,
    # zero rows in the results indicates the failure to obtain cost for a workflow.
    # Second condition applies to 'non-detailed' query, because the results are
    # aggregated there will always be one row minimum, so this condition will confirm
    # the results for that row is not 'None'.
    if query_results.total_rows == 0 or (
            query_results.total_rows == 1 and next(query_job.result()).get(
            "cost") is None):
        LOGGER.error("Could not retrieve cost - no cost entries found.")
        raise ValueError("Could not retrieve cost - no cost entries found.")
    else:
        return query_results


def minimum_time_passed_since_workflow_completion(
    end_time: str, min_hours: int = 24
) -> (bool, datetime):
    """
    Make sure 24 hours have passed between job finish time and executing this command
    (finished time minus current time).

    :param end_time: Workflow completion time obtained from cromwell job metadata
    :param min_hours: Minimum hours after workflow finished in order to perform query
    :return:
    """

    delta = datetime.now(timezone.utc) - datetime.strptime(
        end_time, "%Y-%m-%dT%H:%M:%S.%f%z"
    )

    mindelta = timedelta(hours=min_hours)

    return (True, delta) if delta > mindelta else (False, delta)


def get_submission_start_end_time(workflow_metadata: dict) -> (str, str):
    """
    Gets the start and end time from the workflow metadata.

    :param workflow_metadata:
    :return:
    """

    # If server was restarted multiple start/end times can be present, here we use
    # the earliest value.
    events = workflow_metadata['workflowProcessingEvents']
    try:
        end_time = \
        [i.get("timestamp") for i in events if i.get("description") == "Finished"][0]
    except IndexError:
        end_time = None

    try:
        start_time = \
            [i.get("timestamp") for i in events if i.get("description") == "PickedUp"][0]
    except IndexError:
        start_time = None

    return start_time, end_time


def checks_before_query(start_time: str, end_time: str, workflow_id: str) -> None:
    """
    Check that workflow has finished, and it has finished at least 24 hours from the
    execution of this script.

    :param start_time: Time workflow started
    :param end_time: Time workflow finished
    :param workflow_id:
    :return:
    """

    if not start_time:
        LOGGER.error("Start time was not found for workflow id: %s , which may"
                     "indicate the workflow was recently submitted and has not "
                     "started yet. Cost can only be obtained 24hrs after workflow"
                     "completion.", workflow_id)
        exit()

    if not end_time:
        LOGGER.error("Finished time was not found. Workflow %s is likely running and "
                     "is not finished yet.",
                     workflow_id)
        exit()

    minimum_time_passed, workflow_time_delta = minimum_time_passed_since_workflow_completion(
        end_time=end_time)

    if not minimum_time_passed:
        wait_time: timedelta = (timedelta(hours=24) - workflow_time_delta)
        wait_hours, remainder = divmod(wait_time.seconds, 3600)
        wait_minutes, wait_seconds = divmod(remainder, 60)

        LOGGER.error("Workflow finished less than 24 hours ago.  Cannot check cost.  "
                     "Please wait %sh:%sm:%ss and try again.", wait_hours, wait_minutes,
                     wait_seconds
                     )
        exit()


def round_cost_values(query_rows: list[dict]) -> list[dict]:
    """
    Round the cost value to 2 decimal points and set minimum cost values to .01

    :param query_rows: [dict{"cost"},dict{"cost"},...]
    :return: [dict{"cost"},dict{"cost"},...]
    """

    cost_rounded: list = []

    for row in query_rows:
        if row["cost"] is not None:
            cost = round(float(row["cost"]), 2)
            row["cost"] = max(cost, .01)
            cost_rounded.append(row)

    return cost_rounded


def color_cost_outliers(query_rows_cost_rounded: list[dict]) -> list[dict]:
    """
    Colors cost outliers red. Outliers are defined as cost values
    with a z score that fall outside of 1 standard deviation.

    :param query_rows_cost_rounded: [dict{"cost"},dict{"cost"},...]
    :return: [dict{"cost"},dict{"cost"},...]
    """

    all_task_cost = [row.get("cost") for row in query_rows_cost_rounded]
    mean_cost = statistics.mean(all_task_cost)
    std_cost = statistics.stdev(all_task_cost)

    threshold = 1
    highlighted_query_rows_cost_rounded = []

    for y in query_rows_cost_rounded:
        row_cost = y.get("cost")
        z_score = (row_cost - mean_cost) / std_cost
        if abs(z_score) > threshold:
            highlighted_row = y
            highlighted_row["cost"] = "\033[91m" + str(row_cost) + "\033[0m"
            highlighted_query_rows_cost_rounded.append(highlighted_row)
        else:
            highlighted_query_rows_cost_rounded.append(y)

    return highlighted_query_rows_cost_rounded
