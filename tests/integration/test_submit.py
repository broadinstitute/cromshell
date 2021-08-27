import subprocess

import pytest


class TestSubmit:
    def test_submit(self, local_cromwell_url: str):

        result = subprocess.run(
            [
                "cromshell",
                "--cromwell_url",
                local_cromwell_url,
                "submit",
                "tests/workflows/helloWorld.wdl",
                "tests/workflows/helloWorld.json",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        print(result.stdout.decode("utf-8"))

        if result.stderr is not None:
            print(result.stderr.decode("utf-8"))

        assert result.returncode == 0

    @pytest.fixture
    def local_cromwell_url(self):
        return "http://localhost:8000"
