from cromshell.utilities import http_utils
from importlib import reload
from pathlib import Path
import pytest
import os
from requests.models import Response


class TestHTTPUtilities:
    """Test http_utils  functions and variables"""

    def test_check_http_request_status_code(
            self, mock_failed_response, mock_pass_response
    ):

        # asserts that an exception is raised by the function
        try:
            http_utils.check_http_request_status_code(
                short_error_message="TEST", response=mock_pass_response
            )
        except Exception as exc:
            assert False, f"Function should not have raised any exception {exc}"

        # asserts that an exception is raised by the function
        with pytest.raises(Exception):
            http_utils.check_http_request_status_code(
                short_error_message="TEST", response=mock_failed_response
            )

    @pytest.fixture
    def mock_pass_response(self):
        """Create requests response object to be hold mock response"""

        response = Response()
        response.ok = True
        response.reason = "Reason Mock pass"
        response.status_code = 200
        response.text = "Text Mock"

        return response

    @pytest.fixture
    def mock_failed_response(self):
        """Create requests response object to be hold mock response"""

        response = Response()
        response.ok = False
        response.reason = "Reason Mock failure"
        response.status_code = 400
        response.text = "Text Mock failure"

        return response
