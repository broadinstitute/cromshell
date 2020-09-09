import logging
import pkgutil
from pathlib import Path


def configure_logging(verbosity):
    """Set up logging for the cromshell module"""

    import cromshell  # pylint: disable=C0415

    format_string = get_logging_format_string(cromshell)

    # Set logging level:
    log_level = logging.INFO
    if verbosity:
        log_level = verbosity

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
