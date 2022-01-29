from traceback import print_exception

from click.testing import CliRunner

from cromshell.__main__ import main_entry as cromshell


def run_cromshell_command(command: list, exit_code: int):
    """
    Run cromshell alias using CliRunner and assert job is successful

    :param command: The subcommand, options, and arguments in list form e.g.
    [
        "alias",
        "--",
        workflow_id,
        alias_name,
    ]
    :param exit_code: The expected exit code
    :return: results from execution
    """

    runner = CliRunner(mix_stderr=False)
    # The absolute path will be passed to the invoke command because
    # the test is being run in temp directory created by CliRunner.
    with runner.isolated_filesystem():
        result = runner.invoke(cromshell, command)
        assert result.exit_code == exit_code, (
            f"\nSTDOUT:\n{result.stdout}"
            f"\nSTDERR:\n{result.stderr}"
            f"\nExceptions:\n{result.exception}"
            f"\n{print_exception(*result.exc_info)}"
        )
        return result
