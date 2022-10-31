import re
import sys
from argparse import ArgumentParser, Namespace
from collections.abc import Sequence
from pathlib import Path
from typing import Any, Final, IO, NamedTuple

from rich.console import Console, ConsoleRenderable, Group
from rich.markup import escape
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from dsv_scripts import get_script_name, utils


class _Option(NamedTuple):
    """A `NamedTuple` containing information about an option for a `FileIOParser`."""

    abbreviation: str
    full_name: str
    description: str
    metavar: str | None


class FileIOParser(ArgumentParser):
    """A specialized `ArgumentParser` for scripts that deal with file input & output."""

    def __init__(
        self,
        module_file: str,
        *file_exts: str,
        add_copy_option: bool = True,
        add_force_option: bool = True,
        **kwargs: Any,
    ) -> None:
        """Initializes a new `FileIOParser` instance.

        Args:
            module_file:
                A string containing the file path for the script module.
                Will be parsed to determine the program name to display for the script.
            *file_exts:
                Strings representing the file extensions to process (case-insensitive).
                If omitted, **all** file extensions will be included for processing.
            add_copy_option:
                Whether to include the `-c` or `--copy` option. Defaults to `True`.
            add_force_option:
                Whether to include the `-f` or `--force` option. Defaults to `True`.
            **kwargs:
                Keyword arguments to be forwarded to the `ArgumentParser` constructor.
        """
        super().__init__(prog=get_script_name(module_file), add_help=False, **kwargs)

        self.arg_name: Final[str] = "paths"
        self.arg_description: Final[str] = (
            f"Paths to specific{(' .' + ' or .'.join(file_exts)) if file_exts else ''} "
            f"files.\nIf omitted, will scan the current directory."
        )
        self.file_exts: Final[tuple[str, ...]] = file_exts
        self.options: Final[list[_Option]] = []

        self.add_argument(
            self.arg_name,
            help=self.arg_description,
            metavar=self.arg_name.upper(),
            nargs="*",
        )

        def add_option(raw_name: str, description: str, **option_kwargs: Any) -> None:
            names = (f"-{raw_name[0]}", f"--{raw_name}")
            self.options.append(
                _Option(*names, description, option_kwargs.get("metavar"))
            )
            self.add_argument(*names, help=description, **option_kwargs)

        for name, metavar in [("input", "IN"), ("output", "OUT")]:
            add_option(name, f"Name of the {name} folder.", default="", metavar=metavar)

        if add_copy_option:
            add_option(
                "copy", "Files to copy as-is from input to output.", metavar="REGEX"
            )
        if add_force_option:
            add_option(
                "force", "Force execute. (May overwrite files!)", action="store_true"
            )

        add_option("verbose", "Enable verbose console output.", action="store_true")
        add_option("help", "Show this help message.", action="help")

    def parse_args(  # type: ignore[override]
        self, argv: Sequence[str] | None = None
    ) -> Namespace:
        """Parses/processes the args, and returns a `Namespace` containing the results.

        Attributes of the resulting `Namespace`:
            files (list[tuple[pathlib.Path, pathlib.Path], ...]):
                A list in which each tuple represents the input/output paths for a file.
            logger (logging.Logger):
                A logger initialized with the standard settings for this package.
                (Accounts for the `-v` or `--verbose` command-line option.)
            should_copy (Callable[[Path], bool]):
                A function that returns `True` if the given file should be copied as-is.
                (Accounts for the `-c` or `--copy` command-line option.)

        Args:
            argv:
                A sequence of strings representing the arguments to parse.
                If omitted, `sys.argv` is assumed.
        """
        args = super().parse_args(argv)
        copy = re.compile(getattr(args, "copy", None) or r"$^")  # "$^" never matches.
        logger = utils.get_logger(args.verbose)
        files = []

        input_dir, output_dir = utils.get_input_and_output_dir_paths(
            input_path=args.input,
            output_path=args.output,
            force=getattr(args, "force", True),
        )
        file_paths = utils.get_relevant_file_paths(
            args.paths, *self.file_exts, parent_dir=input_dir, log=logger.info
        )

        for file_path in file_paths:
            output_file = output_dir / file_path
            output_file.parent.mkdir(parents=True, exist_ok=True)
            files.append((input_dir / file_path, output_file))

        logger.info(f"Found {len(files)} files to check and/or process.")

        def should_copy(path: Path) -> bool:
            return copy.search(str(path)) is not None

        return Namespace(files=files, logger=logger, should_copy=should_copy)

    def print_help(self, file: IO[str] | None = None) -> None:
        """Outputs a message containing information about the script and its options.

        Args:
            file:
                A writeable object to which the help message will be sent.
                If omitted, `sys.stdout` is assumed.
        """
        help_elements: list[ConsoleRenderable] = [
            Text(self.description, justify="center"),
            Text("\nUsage:", "bright_magenta"),
        ]
        usage = escape(self.format_usage().replace(" ...", ""))
        usage_text = Text(f"  {usage[usage.index(self.prog):].strip()}")
        help_elements.append(usage_text)

        usage_text.highlight_words([self.prog], f"bright_yellow")
        usage_text.highlight_words([self.arg_name.upper()], f"bright_cyan")
        usage_text.highlight_regex(r"\B-[a-z]", "bright_cyan")
        usage_text.highlight_regex(r"[\[\].]", "bright_black")

        def create_table(title: str) -> Table:
            title_text = Text(f"\n{title}:", "bright_magenta")
            table = Table(box=None, expand=True, padding=0)
            table.add_column(title_text, style="bright_cyan", ratio=1)
            table.add_column(ratio=2)
            help_elements.append(table)
            return table

        arguments_table = create_table("Arguments")
        arguments_table.add_row(f"  {self.arg_name.upper()}", self.arg_description)
        options_table = create_table("Options")

        for option in self.options:
            option_text = Text.assemble(
                f"  {option.abbreviation}", (" | ", "bright_black"), option.full_name
            )
            if option.metavar:
                option_text.append(f" {option.metavar}", "bright_black")
            options_table.add_row(option_text, option.description)

        console = Console(file=file or sys.stdout)
        panel = Panel(
            Group(*help_elements),
            title=Text(self.prog, "bright_yellow"),
            subtitle=Text("dsv-scripts", "bright_black"),
            subtitle_align="right",
            width=min(console.width, 70),
        )
        console.print(panel)
