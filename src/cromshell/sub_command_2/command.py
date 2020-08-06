import logging

import click

LOGGER = logging.getLogger(__name__)


@click.command(name="sub_command_2")
def main():
    """Main entry for Sub Command 2"""
    click.echo("Sub-command 2")
    LOGGER.info("Sub-command 2")
