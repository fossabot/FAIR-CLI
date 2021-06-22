import os
import pathlib


REGISTRY_HOME = os.path.join(pathlib.Path.home(), ".scrc")
FAIR_CLI_CONFIG = "cli-config.yaml"
GLOBAL_CONFIG_DIR = os.path.join(REGISTRY_HOME, "cli")
GLOBAL_FAIR_CONFIG = os.path.join(GLOBAL_CONFIG_DIR, FAIR_CLI_CONFIG)
FAIR_FOLDER = ".fair"


def find_fair_root(start_directory: str = os.getcwd()) -> str:
    """Locate the .fair folder within the current hierarchy

    Parameters
    ----------

    start_directory : str, optional
        starting point for local FAIR folder search

    Returns
    -------
    str
        absolute path of the .fair folder
    """
    _current_dir = start_directory

    # Keep upward searching until you find '.fair', stop at the level of
    # the user's home directory
    while _current_dir != pathlib.Path.home():
        _fair_dir = os.path.join(_current_dir, FAIR_FOLDER)
        if os.path.exists(_fair_dir):
            return os.path.dirname(_fair_dir)
        _current_dir = pathlib.Path(_current_dir).parent
    return ""


def staging_cache() -> str:
    return os.path.join(find_fair_root(), FAIR_FOLDER, "staging")


def data_dir() -> str:
    return os.path.join(REGISTRY_HOME, "data")


def local_fdpconfig() -> str:
    return os.path.join(find_fair_root(), FAIR_FOLDER, FAIR_CLI_CONFIG)


def local_user_config() -> str:
    return os.path.join(find_fair_root(), "config.yaml")


def coderun_dir() -> str:
    return os.path.join(data_dir(), "coderun")
