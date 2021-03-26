import logging
import sys

import requests

from cromshell.utilities import io_utils
from cromshell import log

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
