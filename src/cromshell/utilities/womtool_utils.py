import json
import logging

import requests

import cromshell.utilities.cromshellconfig as cromshellconfig
import cromshell.utilities.http_utils as http_utils
from cromshell import log
from cromshell.utilities.io_utils import dead_turtle

LOGGER = logging.getLogger(__name__)


class ValidationError(Exception):
    """Raised when input WDL or JSON does not pass Womtool Validation"""


def womtool_validate_wdl_and_json(
    wdl: str, wdl_json: str, config: cromshellconfig
) -> None:
    """Validates WDL and input JSON using the Cromwell server's Womtool REST API"""

    LOGGER.info("Validating WDL with with server: %s", config.cromwell_server)
    request_out = womtool_validate_to_server(wdl=wdl, wdl_json=wdl_json, config=config)

    http_utils.check_http_request_status_code(
        short_error_message="Failed to Validate Workflow", response=request_out
    )

    validate_status = json.loads(request_out.content)

    if not validate_status["valid"]:
        log.display_logo(logo=dead_turtle)

        LOGGER.error("Error: Server reports workflow was not valid.")
        raise ValidationError(
            "Error: Server reports workflow was not valid.\n"
            + ("\n".join(validate_status["errors"]))
        )


def womtool_validate_to_server(
    wdl: str, wdl_json: str, config: cromshellconfig
) -> requests.Response:
    with open(wdl, "rb") as wdl_file, open(wdl_json, "rb") as wdl_json_file:
        submission_params = {
            "workflowSource": wdl_file,
            "workflowInputs": wdl_json_file,
        }

        requests_out = requests.post(
            f"{config.get_womtool_api()}/describe",
            files=submission_params,
            timeout=config.requests_connect_timeout,
            verify=config.requests_verify_certs,
            headers=http_utils.generate_headers(config),
        )

        return requests_out
