from cromshell.utilities import http_utils, workflow_id_utils


def resolve_workflow_id_and_server(workflow_id: str, cromshell_config) -> str:
    """
    Resolves the workflow id and sets the cromwell server

    :param workflow_id: workflow UUID, alias, or submission tsv associated int
    :param cromshell_config:
    :return: workflow UUID (hex string)
    """
    resolved_workflow_id = workflow_id_utils.resolve_workflow_id(
        cromshell_input=workflow_id,
        submission_file_path=cromshell_config.submission_file_path,
    )

    http_utils.set_and_check_cromwell_server(
        config=cromshell_config, workflow_id=resolved_workflow_id
    )
    set_workflow_id(workflow_id=resolved_workflow_id, cromshell_config=cromshell_config)

    return resolved_workflow_id


def set_workflow_id(workflow_id: str, cromshell_config) -> None:
    """
    Sets the workflow id in the config object

    :param workflow_id: workflow UUID
    :param cromshell_config:
    :return: None
    """
    cromshell_config.workflow_id = workflow_id
