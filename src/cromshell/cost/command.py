import logging

import click
import cromshell.utilities.command_setup_utils as command_setup_utils
import cromshell.utilities.workflow_id_utils as workflow_id_utils

from datetime import datetime, timezone, timedelta
from tempfile import NamedTemporaryFile
from google.cloud import bigquery
from tabulate import tabulate

LOGGER = logging.getLogger(__name__)


@click.command(name="cost")
@click.argument("workflow_id", required=True)
@click.option(
    "-d",
    "--detailed",
    is_flag=True,
    default=False,
    help="Get the cost for a workflow at the task level",
)
@click.pass_obj
def main(config, workflow_id: str or int, detailed: bool):
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

    check_cost_table_is_configured(config_options=config.cromshell_config_options)

    # Get time workflow finished using metadata command (error if not finished)
    LOGGER.info("Retrieving workflow metadata")
    workflow_metadata = get_metadata(config)
    start_time, end_time = get_submission_start_end_time(workflow_metadata)

    LOGGER.info("Checking workflow completed and finished past 24hrs")
    checks_before_query(end_time=end_time, workflow_id=resolved_workflow_id)

    LOGGER.info("Querying BQ")
    # Create start and end time for query, plus/minus a day from start and finish
    query_start_time = str(datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S.%f%z") - timedelta(days=1))
    query_end_time = str(datetime.strptime(end_time, "%Y-%m-%dT%H:%M:%S.%f%z") + timedelta(days=1))

    query_results = query_bigquery(
        workflow_id=resolved_workflow_id,
        bq_database=config.cromshell_config_options["bq_cost_table"],
        start_date=query_start_time,
        end_date=query_end_time,
        detailed=detailed
    )

    temp_query_result_csv = NamedTemporaryFile()
    write_bq_results_to_temp_csv(
        tempfile=temp_query_result_csv, results=query_results, detailed=detailed
    )

    temp_query_result_csv_rounded = NamedTemporaryFile()
    round_cost_values(
        query_result_csv=temp_query_result_csv,
        query_result_csv_rounded=temp_query_result_csv_rounded,
        detailed=detailed
    )

    with open(temp_query_result_csv_rounded.name, 'r') as f:
        print(f.read())
        print("Costs rounded to nearest cent.")


def query_bigquery(
    workflow_id: str,
    bq_database: str,
    start_date: str,
    end_date: str,
    detailed: bool
):
    """
        Query bigqueury for cost

    :param detailed:
    :param workflow_id:
    :param bq_database:
    :param start_date:
    :param end_date:
    :return:
    """

    client = bigquery.Client()

    # Todo: remove LIMIT in query
    if detailed:
        query = f"""
                SELECT wfid.value, service.description, task.value as task_name, sum(cost) as cost
                FROM {bq_database} as billing, UNNEST(labels) as wfid, UNNEST(labels) as task
                WHERE cost > 0
                AND task.key LIKE "wdl-task-name"
                AND wfid.key LIKE "cromwell-workflow-id"
                AND wfid.value like @workflow_id
                AND partition_time BETWEEN @start_date AND @end_date
                GROUP BY 1,2,3
                ORDER BY 4 DESC
                LIMIT 100
            """
    else:
        query = f"""
                SELECT sum(cost) as cost
                FROM {bq_database}, UNNEST(labels)
                WHERE value LIKE @workflow_id AND partition_time BETWEEN @start_date AND @end_date
                LIMIT 100
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
    if query_results.total_rows == 0 or (query_results.total_rows == 1 and next(query_job.result()).get("cost") is None):
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

    :param end_time: workflow completion time obtained from cromwell job metadata
    :param min_hours:
    :return:
    """

    delta = datetime.now(timezone.utc) - datetime.strptime(
        end_time, "%Y-%m-%dT%H:%M:%S.%f%z"
    )

    mindelta = timedelta(hours=min_hours)

    return (True, delta) if delta > mindelta else (False, delta)


def check_cost_table_is_configured(config_options: dict) -> None:
    if "bq_cost_table" not in config_options:
        raise KeyError('Cromshell config file is missing "bq_cost_table" Key')

    LOGGER.info("Using cost table: %s", config_options["bq_cost_table"])


def get_metadata(config: object) -> dict:
    import cromshell.metadata.command as metadata_command
    from cromshell.utilities import http_utils

    formatted_metadata_parameter = metadata_command.format_metadata_params(
        list_of_keys=config.METADATA_KEYS_TO_OMIT,
        exclude_keys=True,
        expand_subworkflows=False,
    )

    return metadata_command.get_workflow_metadata(
        meta_params=formatted_metadata_parameter,
        api_workflow_id=config.cromwell_api_workflow_id,
        timeout=config.requests_connect_timeout,
        verify_certs=config.requests_verify_certs,
        headers=http_utils.generate_headers(config),
    )


def get_submission_start_end_time(workflow_metadata: dict) -> (str, str):

    events = workflow_metadata['workflowProcessingEvents']
    try:
        end_time = [i.get("timestamp") for i in events if i.get("description") == "Finished"][0]
    except IndexError:
        end_time = None

    start_time = [i.get("timestamp") for i in events if i.get("description") == "PickedUp"][0]

    return start_time, end_time


def checks_before_query(end_time: str, workflow_id: str) -> None:
    """
    Check that workflow has finished, and it has finished at least 24 hours from the
    execution of this script.

    :param end_time:
    :param workflow_id:
    :return:
    """

    if not end_time:
        LOGGER.error("Finished time was not found. Workflow %s is not finished yet.",
                     workflow_id)
        raise ValueError(
            f"Finished time was not found. Workflow {workflow_id} is not finished yet."
        )

    minimum_time_passed, workflow_time_delta = minimum_time_passed_since_workflow_completion(end_time=end_time)

    if not minimum_time_passed:
        wait_time: timedelta = (timedelta(hours=24) - workflow_time_delta)
        wait_hours, remainder = divmod(wait_time.seconds, 3600)
        wait_minutes, wait_seconds = divmod(remainder, 60)

        LOGGER.error("Workflow finished less than 24 hours ago.  Cannot check cost.  "
                     "Please wait %sh:%sm:%ss and try again.", wait_hours, wait_minutes, wait_seconds
                     )
        print(
            f"Workflow finished less than 24 hours ago.  Cannot check cost. "
            f"Please wait {wait_hours}h:{wait_minutes}m:{wait_seconds}s and try again."
        )
        exit()


def write_bq_results_to_temp_csv(tempfile, results, detailed: bool):

    import csv

    with open(tempfile.name, 'w') as tempfile_tsv:

        if detailed:
            # create the csv writer
            writer = csv.DictWriter(tempfile_tsv, delimiter="\t",
                                    fieldnames=["value", "description", "task_name",
                                                "cost"])

            writer.writeheader()

            for row in results:
                writer.writerow(row)

        else:
            writer = csv.DictWriter(
                tempfile_tsv, delimiter="\t", fieldnames=["cost"]
            )

            writer.writeheader()

            for row in results:
                writer.writerow(row)


def round_cost_values(query_result_csv, query_result_csv_rounded, detailed):

    import csv

    field_names = ["value", "description", "task_name", "cost"] if detailed else ["cost"]

    with open(query_result_csv.name, 'r') as tempfile_1, open(query_result_csv_rounded.name, 'w') as tempfile_2:

        writer = csv.DictWriter(tempfile_2, delimiter="\t", fieldnames=field_names)
        reader = csv.DictReader(tempfile_1, delimiter="\t", fieldnames=field_names)
        writer.writeheader()
        for row in reader:
            if row["cost"] is not None:
                if row["cost"] != "cost":
                    cost = round(float(row["cost"]), 2)
                    if cost >= .01:
                        row["cost"] = cost
                    else:
                        row["cost"] = .01

                    writer.writerow(row)
