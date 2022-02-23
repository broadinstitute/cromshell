from cromshell.utilities import cromshellconfig
from cromshell.utilities import submissions_file_utils as sfu


class TestSubmissionsFileUtils:
    """Test the submission_file_utils config functions and variables"""

    def test_get_submission_file_headers(self):
        mutable_headers = [column.value for column in sfu.MutableSubmissionFileHeader]
        immutable_headers = [
            column.value for column in sfu.ImmutableSubmissionFileHeader
        ]
        all_headers = immutable_headers + mutable_headers
        assert cromshellconfig.get_submission_file_headers() == all_headers
