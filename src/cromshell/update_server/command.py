import logging
import click
import json
from pathlib import Path
import os


LOGGER = logging.getLogger(__name__)
CROMWELL_SERVER_KEY = 'cromwell_server'


@click.command(name="update-server")
@click.argument("cromwell_server_url", required=True, nargs=1)
@click.pass_obj
def main(config, cromwell_server_url):
    """Update the default Cromwell server in the config file"""

    # location of the config file
    cromshell_config_path = os.path.join(config.config_dir,
                                         config.CROMSHELL_CONFIG_FILE_NAME)
    assert os.access(cromshell_config_path, mode=os.W_OK), \
        f"Cannot write to Cromshell config file {cromshell_config_path}"

    # the contents of the config file as a dict
    cromshell_config_dict = config.cromshell_config_options

    # update the cromwell server
    if CROMWELL_SERVER_KEY not in cromshell_config_dict.keys():
        cromshell_config_dict.update({CROMWELL_SERVER_KEY: cromwell_server_url})
    else:
        cromshell_config_dict[CROMWELL_SERVER_KEY] = cromwell_server_url

        # write the modified config file
        config_contents = json.dumps(cromshell_config_dict, indent=2)
        with Path(cromshell_config_path).open("w") as crom_config_file:
            crom_config_file.write(config_contents)

    LOGGER.info(f"Cromshell config file at {cromshell_config_path}")
    LOGGER.info(f"Default Cromwell server updated to {cromwell_server_url}")
