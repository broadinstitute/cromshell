from tests.integration import utility_test_functions


class TestVersion:
    """Test the version command."""

    def test_version(self, get_current_version):
        version_result = utility_test_functions.run_cromshell_command(
            command=["version"],
            exit_code=0,
        )

        print("Print version results:")
        print(version_result.stdout)

        assert version_result.stdout == "cromshell " + get_current_version + "\n"
