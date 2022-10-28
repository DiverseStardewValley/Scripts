"""This module is the primary entry point (`dsv-scripts` or `python -m dsv_scripts`)."""
from __future__ import annotations

from importlib.metadata import metadata
from typing import Final

from dsv_scripts import commands

_HEADER_LINES: Final[tuple[tuple[str, str], ...]] = (
    (r"      _                            _       _        ", "bright_red"),
    (r"   __| |_____   __   ___  ___ _ __(_)_ __ | |_ ___  ", "bright_red"),
    (r"  / _` / __\ \ / /__/ __|/ __| '__| | '_ \| __/ __| ", "bright_yellow"),
    (r" | (_| \__ \\ V /___\__ \ (__| |  | | |_) | |_\__ \ ", "bright_green"),
    (r"  \__,_|___/ \_/    |___/\___|_|  |_| .__/ \__|___/ ", "bright_cyan"),
    (r"                                    |_| ", "bright_cyan"),
)


def main() -> int:
    """Primary entry function. Parses args and calls the appropriate script/callback."""
    get_metadata = metadata("dsv-scripts").json.get
    parser = commands.CommandParser(
        *_HEADER_LINES,
        version=get_metadata("version"),
        description=get_metadata("summary"),
    )
    parser.set_defaults(callback=parser.print_help)

    expected_args, extra_args = parser.parse_known_args()
    return expected_args.callback(extra_args) or 0


if __name__ == "__main__":
    raise SystemExit(main())
