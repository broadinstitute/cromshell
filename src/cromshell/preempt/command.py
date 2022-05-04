import logging

import click
import requests
import json
import subprocess

from cromshell.metadata.command import obtain_metadata, check_cromwell_server
from cromshell.utilities import (
    cromshellconfig, http_utils, io_utils, workflow_id_utils
)

LOGGER = logging.getLogger(__name__)


@click.command(name="preempt")
@click.option("--workflow", default=None, nargs=1,
              help="Cromwell workflow specifying the job. Can be a workflow_id "
                   "or a digit (-1 for last, -2 for second-last, etc.) or "
                   "a workflow alias")
@click.option("--task", default=None, nargs=1,
              help="Cromwell task name (within the specified workflow). "
                   "If unspecified, will look for the latest "
                   "preemptible task in the workflow")
@click.option("-v", "--verbose", default=False, is_flag=True,
              help="Print the output of the 'gcloud compute instances stop' command")
@click.pass_obj
def main(config, workflow, task, verbose):
    """Preempt a machine currently running a task."""

    LOGGER.info("preempt")

    # TODO: alternative approach
    # system command
    # gcloud compute instances list --filter='labels.cromwell-workflow-id:cromwell-{WORKFLOW_ID} labels.wdl-task-name:{TASK}' --format 'table(name)'

    # input validation and extraction of actual workflow_id
    workflow_id = workflow_id_utils.resolve_workflow_id(workflow)

    return_code = 0

    # update the internal cromwell server based on the workflow,
    # set the workflow_id as a config attribute, and assert communication
    # with the server
    check_cromwell_server(config=config, workflow_id=workflow_id)

    # TODO check status
    # this could be done using the metadata, not as a separate call
    # accessed via metadata_dict['status']

    # TODO which task is running
    # this can be accessed via metadata_dict['calls'][task][-1]['backendStatus']

    # obtain metadata for workflow (relying on config attributes) as dict
    metadata_json_string = obtain_metadata(
        config=config,
        metadata_param=[],
        exclude_keys=False,
        dont_expand_subworkflows=False,
    )
    metadata_dict = json.loads(metadata_json_string)

    # identify the task
    all_tasks = metadata_dict['calls'].keys()
    if task is None:
        task = all_tasks[-1]
    elif task not in all_tasks:
        LOGGER.error(f"Specified task {task} not in metadata.  "
                     f"Tasks which appear: [{all_tasks}]")
        return_code = 1

    # identify the machine (-1 is for the latest attempt, I think)
    machine_info_dict = metadata_dict['calls'][task][-1]['jes']
    machine_name = machine_info_dict['instanceName']
    zone = machine_info_dict['zone']
    billing_project = machine_info_dict['googleProject']

    # preempt the machine
    cmd = ['gcloud', 'compute', 'instances', 'stop', machine_name,
           '--zone', zone, '--billing-project', billing_project]
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
        if verbose:
            LOGGER.info(out.decode())

    except subprocess.CalledProcessError as e:
        LOGGER.error(f"There was an error running the stop command:\n"
                     f"{' '.join(cmd)}")
        LOGGER.error(e)
        LOGGER.error(e.stdout.decode())
        return_code = 1

    return return_code
