import pytest
from requests.models import Response

from cromshell.utilities import http_utils


class TestHTTPUtilities:
    """Test http_utils  functions and variables"""

    def test_check_http_request_status_code(
        self, mock_failed_response, mock_pass_response
    ):

        # asserts that an exception is raised by the function
        http_utils.check_http_request_status_code(
            short_error_message="TEST", response=mock_pass_response
        )

        # asserts that an exception is raised by the function
        with pytest.raises(Exception):
            http_utils.check_http_request_status_code(
                short_error_message="TEST", response=mock_failed_response
            ), "If response.ok is False then exception should be raised"

    @pytest.fixture
    def mock_pass_response(self):
        """Create requests response object to be hold mock response"""

        response = Response()
        response.reason = "Reason Mock pass"
        response.status_code = 200

        return response

    @pytest.fixture
    def mock_failed_response(self):
        """Create requests response object to be hold mock response"""

        response = Response()
        response.reason = "Reason Mock failure"
        response.status_code = 400

        return response
