import logging

import requests

from cromshell import log
from cromshell.utilities import io_utils

LOGGER = logging.getLogger(__name__)


def assert_can_communicate_with_server(config):
    """Check Connection with Cromwell Server"""

    try:
        request_out = requests.get(
            f"{config.cromwell_api}/backends",
            timeout=config.requests_connect_timeout,
            verify=config.requests_verify_certs,
        )
    except ConnectionError:
        LOGGER.error("Failed to connect to %s", config.cromwell_server)
        raise Exception("Failed to connect to %s", config.cromwell_server)
    except requests.exceptions.RequestException:
        LOGGER.error("Failed to connect to %s", config.cromwell_server)
        raise Exception(f"Failed to connect to {config.cromwell_server}")

    if b"supportedBackends" not in request_out.content:
        log.display_logo(io_utils.dead_turtle)
        LOGGER.error(
            "Error: Cannot communicate with Cromwell server: %s", config.cromwell_server
        )
        raise Exception(
            "Error: Cannot communicate with Cromwell server: %s", config.cromwell_server
        )


def check_http_request_status_code(
    short_error_message: str, response: requests.models.Response
):
    """Check request response "ok" key. Response.ok returns
    False if status_code is equal to or greater than 400.

    - short_error_message: simple version of error message
    - response: output from request
    """

    if not response.ok:
        LOGGER.error(f"{short_error_message}")
        LOGGER.error(f"Reason: {response.reason}")
        LOGGER.error(f"Status_code: {response.status_code}")
        LOGGER.error(f"Message: {response.text}")
        raise Exception(
            f"{short_error_message}\n"
            f"Reason: {response.reason}\n"
            f"Status_code: {response.status_code}\n"
            f"Message: {response.text}"
        )
