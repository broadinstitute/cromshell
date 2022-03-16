import logging
from subprocess import check_output

import requests

from cromshell import log
from cromshell.utilities import cromshellconfig, io_utils

LOGGER = logging.getLogger(__name__)


def assert_can_communicate_with_server(config):
    """Check Connection with Cromwell Server"""

    try:
        request_out = requests.get(
            f"{config.get_cromwell_api()}/backends",
            timeout=config.requests_connect_timeout,
            verify=config.requests_verify_certs,
            headers=generate_headers(config),
        )
    except ConnectionError:
        LOGGER.error("Failed to connect to %s", config.cromwell_server)
        raise Exception(f"Failed to connect to {config.cromwell_server}")
    except requests.exceptions.RequestException:
        LOGGER.error("Failed to connect to %s", config.cromwell_server)
        raise Exception(f"Failed to connect to {config.cromwell_server}")

    if b"supportedBackends" not in request_out.content:
        log.display_logo(io_utils.dead_turtle)
        LOGGER.error(
            "Error: Cannot communicate with Cromwell server: %s due to error: \n%s",
            config.cromwell_server,
            request_out.content,
        )
        raise Exception(
            f"Error: Cannot communicate with Cromwell server: {config.cromwell_server} due to error {request_out.content}"
        )


def check_http_request_status_code(
    short_error_message: str,
    response: requests.models.Response,
    raise_exception: bool = True,
):
    """Check request response "ok" key value. If status_code is
    equal to or greater than 400 Response.ok returns
    False and checker function will fail with error.

    - short_error_message: simple version of error message
    - response: output from request
    """

    if not response.ok:
        LOGGER.error(short_error_message)
        LOGGER.error("Reason: %s", response.reason)
        LOGGER.error("Status_code: %s", response.status_code)
        LOGGER.error("Message: %s", response.text)
        if raise_exception:
            raise requests.exceptions.RequestException(
                f"{short_error_message}\n"
                f"Reason: {response.reason}\n"
                f"Status_code: {response.status_code}\n"
                f"Message: {response.text}"
            )


def generate_headers(config):
    """
    Check the config for options that require a header and generate the appropriate map.
    Will be an empty map if no relevant options are specified.
    """
    headers = {}

    if config.referer_header_url is not None:
        headers["Referer"] = config.referer_header_url

    if config.gcloud_token_email is not None:
        out = check_output(  # Grab output, or raise error & halt Cromshell if nonzero exit code
            [
                "gcloud",
                "auth",
                f"--account={config.gcloud_token_email}",
                "print-access-token",
            ],
        )

        token = out.decode("utf-8").strip()  # Decode bytes, strip trailing newline
        headers["Authorization"] = f"Bearer {token}"

    return headers


def set_and_check_cromwell_server(config, workflow_id):
    """Checks for an associated cromwell server for the workflow_id
    and checks connection with the cromwell server"""

    # Overrides the default cromwell url set in the cromshell config file or
    # command line argument if the workflow id is found in the submission file.
    cromshellconfig.resolve_cromwell_config_server_address(workflow_id=workflow_id)

    config.cromwell_api_workflow_id = f"{config.get_cromwell_api()}/{workflow_id}"

    # Check if Cromwell Server Backend works
    assert_can_communicate_with_server(config)
