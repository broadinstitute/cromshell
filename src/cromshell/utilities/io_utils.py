from termcolor import colored


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
        print(colored("=================     ===============     ===============   ========  ========", "red"))
        print(colored("\\\\ . . . . . . .\\\\   //. . . . . . .\\\\   //. . . . . . .\\\\  \\\\. . .\\\\// . . //", "red"))
        print(colored("||. . ._____. . .|| ||. . ._________________________. . .|| || . . .\\/ . . .||", "red"))
        print(colored("|| . .||   ||. . || || . ./|  ,,    ,,     ,,      |\\. . || ||. . . . . . . ||", "red"))
        print(colored("||. . ||   || . .|| ||. . ||  \\‾\\,-/‾/====/‾/,     || . .|| || . | . . . . .||", "red"))
        print(colored("|| . .||   ||. _-|| ||-_ .||   \\/=<‾><‾><‾><‾>-,   ||. _-|| ||-_.|\\ . . . . ||", "red"))
        print(colored("||. . ||   ||-'  || ||  `-||   / (\\‾\\‾|‾/‾/‾/‾     ||-'  || ||  `|\\_ . .|. .||", "red"))
        print(colored("|| . _||   ||    || ||    ||  \\‾x/ ˙'-;-;-'˙       ||    || ||   |\\ `-_/| . ||", "red"))
        print(colored("||_-' ||  .|/    || ||    \\|_______________________|/    || ||   | \\  / |-_.||", "red"))
        print(colored("||    ||_-'      || ||      `-_||    || ||    ||_-'      || ||   | \\  / |  `||", "red"))
        print(colored("||    `'         || ||         `'    || ||    `'         || ||   | \\  / |   ||", "red"))
        print(colored("||            .===' `===.         .==='.`===.         .===' /==. |  \\/  |   ||", "red"))
        print(colored("||         .=='   \\_|-_ `===. .==='   _|_   `===. .===' _-|/   `==  \\/  |   ||", "red"))
        print(colored("||      .=='    _-'    `-_  `='    _-'   `-_    `='  _-'   `-_  /|  \\/  |   ||", "red"))
        print(colored("||   .=='    _-'          `-__\\._-'         `-_./__-'         `' |. /|  |   ||", "red"))
        print(colored("||.=='    _-'                                                     `' |  /==.||", "red"))
        print(colored("=='    _-'                                                            \\/   `==", "red"))
        print(colored("\\   _-'                                                                `-_   /", "red"))
        print(colored(".`''                                                                      ``'.", "red"))
