import logging

import click

LOGGER = logging.getLogger(__name__)


@click.command(name="sub_command_3", hidden=True)
def main():
    """Main entry for Sub Command 3 - the hidden sub-command."""
    click.echo("Sub-command 3")
    LOGGER.info("Sub-command 3")
