from types import ModuleType

from dsv_scripts.commands import CommandParser


def get_script_modules() -> list[ModuleType]:
    """Returns a list containing the modules that implement `dsv-scripts` commands."""
    return []


__all__ = [
    "CommandParser",
    "get_script_modules",
]
