import logging
import sys

import requests

from cromshell.utilities import IOUtils

LOGGER = logging.getLogger(__name__)


def assert_can_communicate_with_server(cromshell_url):
    """Check Connection with Cromwell Server"""

    try:
        curl_out = requests.get("{}/api/workflows/v1/backends".format(cromshell_url))
    except ConnectionError:
        LOGGER.error("Failed to connect to %s", cromshell_url)
        sys.exit()
    except requests.exceptions.RequestException:
        raise Exception("Failed to connect to {}".format(cromshell_url)) from None

    if b"supportedBackends" not in curl_out.content:
        IOUtils.turtle_dead(cromshell_url.is_verbose)
        LOGGER.error(
            "Error: Cannot communicate with Cromwell server: %s", cromshell_url
        )
        sys.exit()
