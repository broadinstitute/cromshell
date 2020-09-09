from pathlib import Path

from termcolor import colored


def copy_file(source, destination):
    source_path = Path(source)
    destination_path = Path(destination)
    destination_path.write_bytes(source_path.read_bytes())


def turtle_dead(show_logo):
    """Print Dead Turtle"""
    if show_logo:
        print(colored("    ,,    ,,     ,,      ", "red"))
        print(colored("    \\‾\\,-/‾/====/‾/,   ", "red"))
        print(colored("     \\/=<‾><‾><‾><‾>-,  ", "red"))
        print(colored("     / (\\‾\\‾|‾/‾/‾/‾   ", "red"))
        print(colored("    \\‾x/ ˙'-;-;-'˙      ", "red"))
        print(colored("     ‾‾                  ", "red"))


def turtle(show_logo):
    """Print Alive Turtle"""
    if show_logo:
        print(colored("                  __         ", "green"))
        print(colored("       .,-;-;-,. /'_\\       ", "green"))
        print(colored("     _/_/_/_|_\\_\\) /       ", "green"))
        print(colored("   '-<_><_><_><_>=/\\        ", "green"))
        print(colored("     \\`/_/====/_/-'\\_\\    ", "green"))
        print(colored('       ""     ""    ""       ', "green"))


def doomed_logo(show_logo):
    """Print Doom """
    if show_logo:
        print(colored("______     ______    ______  ____  ___      ", "red"))
        print(colored("\\   _ \\   /  __  \\  /  __  \\ \\   \\/  |", "red"))
        print(colored(" | | | |  | |  | |  | |  | |  | |\\/| |     ", "red"))
        print(colored(" | | | |  | |  | |  | |  | |  | |  | |      ", "red"))
        print(colored(" | |/ /   \\  \\/  /  \\  \\/  /  \\ |  | | ", "red"))
        print(colored(" |   /     \\    /    \\    /    \\|  | |   ", "red"))
        print(colored(" |  /       \\__/      \\__/         | |    ", "red"))
        print(colored(" | /                               \\ |     ", "red"))
        print(colored(" |/                                 \\|     ", "red"))
