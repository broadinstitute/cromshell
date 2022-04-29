import os
from traceback import print_exception

from click.testing import CliRunner

from cromshell.__main__ import main_entry as cromshell
from cromshell.utilities.cromshellconfig import (
    CROMSHELL_CONFIG_FILE_NAME,
    __load_cromshell_config_file,
    config_dir,
)


def get_current_cromwell_server():
    cromshell_config_dict = __load_cromshell_config_file(
        config_directory=config_dir,
        config_file_name=CROMSHELL_CONFIG_FILE_NAME,
        config_file_template=None,
    )
    print(os.path.join(config_dir, CROMSHELL_CONFIG_FILE_NAME))
    print(cromshell_config_dict)
    return cromshell_config_dict["cromwell_server"]


def run_update_server(runner, new_cromwell_server):
    """Run cromshell update-server in a specific CliRunner context"""

    result = runner.invoke(
        cromshell,
        [
            "update-server",
            new_cromwell_server,
        ],
    )

    # print any exceptions so pytest will show them
    print_exception(*result.exc_info)


def test_update_server():
    """Run cromshell update-server using CliRunner and ensure server changes"""

    print("Running a test of cromshell update-server...")

    test_server_name = "http://test.server"

    runner = CliRunner(mix_stderr=False)
    # The test is being run in temp directory created by CliRunner, and
    # so its modification of the default server only happens in this context
    with runner.isolated_filesystem():

        # the current default server
        current_cromwell_server = get_current_cromwell_server()
        print(f"Initial Cromwell server: {current_cromwell_server}")

        # update the server and check that it worked
        run_update_server(
            runner=runner,
            new_cromwell_server=test_server_name,
        )
        tmp_cromwell_server = get_current_cromwell_server()
        print(
            f"After attempting to update to '{test_server_name}', "
            f"the config file has '{tmp_cromwell_server}'"
        )
        assert tmp_cromwell_server == test_server_name, "cromshell update-server failed"
