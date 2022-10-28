"""This module contains command-related classes for organizing the available scripts."""
from __future__ import annotations

import sys
from argparse import ArgumentParser
from collections.abc import Callable
from types import ModuleType
from typing import Any, Final, IO, NamedTuple

from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


class CommandInfo(NamedTuple):
    """A `NamedTuple` subclass to hold information about an available command/script."""

    name: str
    """The name of the command/script. Must be unique across all commands."""

    description: str
    """A short, human-readable summary of what the command/script does."""

    callback: Callable[[list[str]], int]
    """The function that should be called when this command/script is invoked."""

    @classmethod
    def from_module(cls, module: ModuleType) -> CommandInfo:
        """Initializes a new `CommandInfo` instance based on the given script module."""
        return cls(
            name=getattr(module, "NAME", module.__name__.replace("_", "-")),
            description=getattr(module, "DESCRIPTION", ""),
            callback=getattr(module, "main"),
        )


class CommandParser(ArgumentParser):
    """An `ArgumentParser` for organizing and pretty-printing the available commands."""

    def __init__(self, *header_lines: tuple[str, str], **kwargs: Any) -> None:
        """Initializes a new `CommandParser` instance.

        Args:
            *header_lines:
                Lines of text to display at the top of the `--help` menu for the primary
                entry point. Each argument should be a tuple of two strings. The first
                string should contain the plain text content, and the second string
                should correspond to the `rich` style to be applied to the first string.
            **kwargs:
                Keyword arguments to be forwarded to the `ArgumentParser` constructor.
        """
        version = kwargs.pop("version") or "?.?.?"
        super().__init__(**kwargs)

        self.subparsers: Final[Any] = self.add_subparsers(parser_class=ArgumentParser)
        self.command_info: Final[list[CommandInfo]] = []
        self.header: Final[list[Text]] = [Text(*args) for args in header_lines]

        self.header[-1].append(f"v{version}".ljust(7).center(12), style="bright_black")

    def add_command(self, command_info: CommandInfo) -> None:
        """Adds a command to this parser, making it usable through `dsv-scripts <name>`.

        Args:
            command_info:
                The `CommandInfo` object for the command/script to add.
        """
        subparser = self.subparsers.add_parser(
            command_info.name, help=command_info.description, add_help=False
        )
        subparser.set_defaults(callback=command_info.callback)
        self.command_info.append(command_info)

    def print_help(self, file: IO[str] | None = None) -> None:
        """Outputs a message containing information about the program and its commands.

        Args:
            file:
                A writeable object to which the help message will be sent.
                If omitted, `sys.stdout` is assumed.
        """
        console = Console(file=file or sys.stdout)
        total_width = min(console.width, 70)
        header_width = total_width - 4
        help_elements = []

        for line in self.header:
            line.align("center", header_width)
            help_elements.append(line)

        if self.description:
            help_elements.append(Text(f"\n{self.description}", justify="center"))

        table = Table(title=" ", box=None, expand=True, header_style="bright_magenta")
        help_elements.append(table)

        table.add_column("Command", style="bright_cyan")
        table.add_column("Description")

        for command, description, _ in self.command_info:
            table.add_row(command, description)

        console.print(Panel(Group(*help_elements), width=total_width))
