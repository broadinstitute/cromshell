from src.cromshell.__main__ import print_version


class TestVersion:
    """Test the version command functions."""

    def test_version(self, get_current_version, capsys):
        cromshell_version = get_current_version

        print_version()
        captured = capsys.readouterr()
        assert captured.out == "cromshell " + cromshell_version + "\n"
