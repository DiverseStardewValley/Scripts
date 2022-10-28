"""This module is the primary entry point (`dsv-scripts` or `python -m dsv_scripts`)."""
from __future__ import annotations

from importlib.metadata import metadata
from typing import Final

from rich import print
from rich.text import Text

HEADER: Final[tuple[Text, ...]] = (
    Text(r"      _                            _       _        ", "bright_red"),
    Text(r"   __| |_____   __   ___  ___ _ __(_)_ __ | |_ ___  ", "bright_red"),
    Text(r"  / _` / __\ \ / /__/ __|/ __| '__| | '_ \| __/ __| ", "bright_yellow"),
    Text(r" | (_| \__ \\ V /___\__ \ (__| |  | | |_) | |_\__ \ ", "bright_green"),
    Text(r"  \__,_|___/ \_/    |___/\___|_|  |_| .__/ \__|___/ ", "bright_cyan"),
    Text(r"                                    |_| ", "bright_cyan"),
)


def main() -> int:
    """Prints the package name & version. Will probably add more functionality later."""
    version_text = f"v{metadata('dsv-scripts').json.get('version')}"
    HEADER[-1].append(f"{version_text.ljust(7).center(12)}\n", "bright_black")

    for line in HEADER:
        line.align("center", 60)
        print(line)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
