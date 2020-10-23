import logging
import sys

import requests

from cromshell.utilities import io_utils

LOGGER = logging.getLogger(__name__)


def assert_can_communicate_with_server(config):
    """Check Connection with Cromwell Server"""

    try:
        request_out = requests.get(f"{config.cromwell_server}{config.api_string}backends", timeout=5)
    except ConnectionError:
        LOGGER.error("Failed to connect to %s", config.cromwell_server)
        sys.exit(1)
    except requests.exceptions.RequestException:
        raise Exception(f"Failed to connect to {config.cromwell_server}") from None

    if b"supportedBackends" not in request_out.content:
        io_utils.turtle_dead(config.is_verbose)
        LOGGER.error(
            "Error: Cannot communicate with Cromwell server: %s", config.cromwell_server
        )
        sys.exit(1)
