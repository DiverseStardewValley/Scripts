"""Main package for `dsv-scripts` (https://github.com/DiverseStardewValley/Scripts)."""
from __future__ import annotations

from types import ModuleType


def get_script_modules() -> list[ModuleType]:
    """Returns a list containing the modules that implement `dsv-scripts` commands."""
    return []


def get_script_name(module: ModuleType) -> str:
    """Returns the user-friendly name of the script defined in the given module."""
    return getattr(module, "NAME", module.__name__.replace("_", "-"))


__all__ = [
    "get_script_modules",
    "get_script_name",
]
