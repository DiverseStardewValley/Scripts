"""This package exports tools for parsing & executing all the `dsv-scripts` commands."""
from dsv_scripts.commands import CommandInfo, CommandParser


def get_all_commands() -> list[CommandInfo]:
    """Returns a list of `CommandInfo` objects representing the available scripts."""
    script_modules = []  # type: ignore[var-annotated] # TODO: Implement script modules!
    return [CommandInfo.from_module(module) for module in script_modules]


__all__ = [
    "CommandInfo",
    "CommandParser",
    "get_all_commands",
]
