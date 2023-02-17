import logging
from enum import Enum

LOGGER = logging.getLogger(__name__)


class WorkflowStatuses(Enum):
    """Enum to hold all possible status of workflow"""

    # States listed here: https://github.com/broadinstitute/cromwell/blob/32d5d0cbf07e46f56d3d070f457eaff0138478d5/core/src/main/scala/cromwell/core/WorkflowState.scala

    SUBMITTED = ["Submitted"]
    FAILED = ["Failed", "fail"]
    ABORTED = ["Aborted", "Aborting", "abort"]
    RUNNING = ["Running"]
    SUCCEEDED = ["Succeeded"]
    DOOMED = ["DOOMED"]


class TaskStatus(Enum):
    """Enum to hold all possible status of workflow"""

    FAILED = "Failed"
    RUNNING = "Running"
    DONE = "Done"
    RETRYABLEFAILURE = "RetryableFailure"

    @classmethod
    def list(cls):
        return [key.value for key in cls]


def confirm_workflow_in_terminal_status(workflow_status: str) -> None:
    """

    :param workflow_status:
    :return:
    """
    non_terminal_statuses = [
        WorkflowStatuses.SUBMITTED.value,
        WorkflowStatuses.RUNNING.valu,
    ]

    if workflow_status in non_terminal_statuses:
        LOGGER.error(
            "Workflow status must be in terminal state, workflow status is currently: "
            f"{workflow_status}"
        )
        raise Exception(
            "Workflow status must be in terminal state, workflow status is currently: "
            f"{workflow_status}"
        )
