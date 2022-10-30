"""Main package for `dsv-scripts` (https://github.com/DiverseStardewValley/Scripts)."""
import re
from pathlib import Path


def get_script_module_paths() -> list[Path]:
    """Returns a list of paths to the modules that implement `dsv-scripts` commands."""
    skip_modules = ("commands", "fileio", "utils")
    return [
        path
        for path in Path(__file__).parent.glob("*.py")
        if not (path.stem.startswith("_") or (path.stem in skip_modules))
    ]


def get_script_name(module_file: str | Path) -> str:
    """Returns the user-friendly name of the script defined in the given module file."""
    if module_match := re.search(r"\W([a-z_]+)\.py$", str(module_file)):
        return module_match[1].replace("_", "-")
    else:
        raise ValueError(f"Invalid module file: '{module_file}'")


__all__ = [
    "get_script_module_paths",
    "get_script_name",
]
