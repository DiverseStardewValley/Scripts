"""Main package for `dsv-scripts` (https://github.com/DiverseStardewValley/Scripts)."""
import re
from importlib import import_module
from pathlib import Path
from types import ModuleType


def get_script_modules() -> list[ModuleType]:
    """Returns a list containing the modules that implement `dsv-scripts` commands."""
    package_dir = Path(__file__).parent
    skip_modules = ("commands", "utils")
    return [
        import_module(f"{package_dir.name}.{path.stem}")
        for path in package_dir.glob("*.py")
        if not (path.stem.startswith("_") or (path.stem in skip_modules))
    ]


def get_script_name(module_file: str) -> str:
    """Returns the user-friendly name of the script defined in the given module file."""
    if module_match := re.search(r"\W([a-z_]+)\.py$", module_file):
        return module_match[1].replace("_", "-")
    else:
        raise ValueError(f"Invalid module file: '{module_file}'")


__all__ = [
    "get_script_modules",
    "get_script_name",
]
