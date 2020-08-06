import logging

import click

LOGGER = logging.getLogger(__name__)


@click.command(name="sub_command_1")
def main():
    """Main entry for Sub Command 1"""
    click.echo("Sub-command 1")
    LOGGER.info("Sub-command 1")
