import logging
import pkgutil
from pathlib import Path

LOGGER = logging.getLogger(__name__)

# Default for boolean to display logo
show_logo = True


def override_logo_display_setting(hide_logo):
    """Override boolean for displaying turtle Logo"""

    global show_logo

    if hide_logo is True:
        show_logo = False


def display_logo(logo):
    """Prints logo to screen"""

    if show_logo:
        logo()


def configure_logging(verbosity):
    """Set up logging for the cromshell module"""

    # Having the cromshell import here instead of at the top is for speed optimization
    import cromshell  # pylint: disable=C0415

    format_string = get_logging_format_string(cromshell)

    # Set logging level:
    log_level = logging.WARNING
    if verbosity:
        log_level = int(verbosity)

    # Create our basic config:
    logging.basicConfig(level=log_level, format=format_string)


def get_logging_format_string(package):
    """Get format string for all loggers
    Discovers all modules to determine the space needed to
    nicely format log messages from all modules.
    """
    module_names = get_dot_separated_submodule_names(package)
    max_module_name_length = max(len(name) for name in module_names)
    format_string = (
        f"%(asctime)s %(name)-{max_module_name_length}s %(levelname)-8s %(message)s"
    )
    return format_string


def get_dot_separated_submodule_names(package):
    """Get dot-separated list of package submodules"""
    module_names = []
    for module_info in get_package_paths(package.__path__):
        module_path = module_info.module_finder.path
        module_prefix = module_path.rpartition(package.__name__)[2].lstrip("/")
        module_path = Path(module_prefix) / module_info.name
        module_path_string = str(module_path).replace("/", ".")
        module_names.append(f"{package.__name__}.{module_path_string}")
    return module_names


def get_package_paths(paths):
    """Recursively walk through all child packages of paths
    returns: iterator of ModuleInfo objects
    """
    child_packages = pkgutil.walk_packages(paths)
    for child in child_packages:
        if child.ispkg:
            yield from get_package_paths(
                [str(Path(child.module_finder.path) / child.name)]
            )
        else:
            yield child


class DelayedLogMessage:
    """
    Used to display log messages at a later time.
    This class will save log messages over the course of a command, to be printed
    later. This is useful if messages printed to the screen causes distraction to
    the cromshell commands' normal printout. Saving and printing the log messages offers
    a cleaner look.

    """
    messages = []

    @classmethod
    def save_log_message(cls, log_level: int, log_message: str) -> None:
        """
        Saves log messages and type
        :param log_level: Expects less than 40.
        Representing debug(10), 'info'(20), or 'warning'(30)
        :param log_message: Log message
        :return:
        """

        if log_level > 40:
            LOGGER.error(
                "Functions 'log_type' must either be 'warning', 'info' or 'debug'."
            )
            raise ValueError(
                "Functions 'log_type' must either be 'warning', 'info', or 'debug.'"
            )

        cls.messages.append([log_level, log_message])

    @classmethod
    def display_log_messages(cls) -> None:
        """
        Displays all saved log messages
        :return:
        """

        if cls.messages:
            for m in cls.messages:
                LOGGER.info(f"{m[1]}") if m[0] == "info" else LOGGER.warning(f"{m[1]}")
