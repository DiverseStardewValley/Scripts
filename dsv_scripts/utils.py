import logging
import os
from collections.abc import Callable, Iterable
from pathlib import Path

from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.text import Text


def get_dir_path(raw_path: str, *, create_if_missing: bool = False) -> Path:
    """Returns the resolved (i.e. absolute) `Path` object corresponding to `raw_path`.

    Args:
        raw_path:
            A string representing a path to a "target" directory.
            This path may be absolute or relative to the current working directory.
        create_if_missing:
            Whether to create the target directory (and any required parent directories)
            if it doesn't already exist. Has no effect if the target dir already exists.

    Raises:
        NotADirectoryError: If `raw_path` points to an existing file.
        FileNotFoundError: If `raw_path` does not exist and `create_if_missing`
            is `False`.
    """
    dir_path = Path(raw_path).resolve()

    if dir_path.is_file():
        raise NotADirectoryError(f"Expected a directory, but found a file: {dir_path}")
    elif create_if_missing:
        dir_path.mkdir(parents=True, exist_ok=True)

    if dir_path.is_dir():
        return dir_path
    else:
        raise FileNotFoundError(f"The requested directory does not exist: {dir_path}")


def get_display_path(path: Path, relative_dir: Path | None = None) -> str:
    """Returns a string representing the given path relative to a specific directory.

    Args:
        path:
            The path to represent as a string.
        relative_dir:
            The path to the directory that will serve as the reference point.
            If omitted, the current working directory will be used.
    """
    relative_dir = relative_dir or Path.cwd()
    return (
        f".{os.path.sep}{path.relative_to(relative_dir)}"
        if path.is_relative_to(relative_dir)
        else str(path)
    )


def get_input_and_output_dir_paths(
    input_path: str, output_path: str, *, force: bool = False
) -> tuple[Path, Path]:
    """Returns a tuple containing the `Path` objects for `input_path` and `output_path`.

    Args:
        input_path:
            A string representing the path to the **input** directory.
            This path may be absolute or relative to the current working directory.
        output_path:
            A string representing the path to the **output** directory.
            This path may be absolute or relative to the current working directory.
        force:
            If set to `True`, will attempt to create the input/output directories (if
            they don't already exist), **and** will allow the script to continue even
            if `input_path` and `output_path` point to the same directory.

    Raises:
        NotADirectoryError: If `input_path` and/or `output_path` points to an
            existing file.
        FileNotFoundError: If `input_path` and/or `output_path` does not exist
            and `force` is `False`.
        SystemExit: If `input_path` and `output_path` are identical and `force`
            is `False`. Will be raised with exit code `1`.
    """
    input_dir_path = get_dir_path(input_path, create_if_missing=force)
    output_dir_path = get_dir_path(output_path, create_if_missing=force)

    if (input_dir_path == output_dir_path) and (not force):
        hint_text = Text(
            "(Use -i and -o to set the folders, or -f to bypass this check.)",
            "bright_black",
        )
        hint_text.highlight_regex(r" -[iof] ", "bright_cyan")

        error_text = Text.assemble(
            ("Input and output folders are the same:\n", "bright_red"),
            str(input_dir_path),
            ("\n\nExiting to avoid overwriting any files.\n", "bright_yellow"),
            hint_text,
            justify="center",
        )
        title_text = Text("ERROR", "bright_red")

        panel = Panel(error_text, title=title_text, expand=False, padding=(1, 2))
        Console().print(panel)
        raise SystemExit(1)

    return input_dir_path, output_dir_path


def get_logger(verbose: bool = False) -> logging.Logger:
    """Returns a pre-configured logger that uses the standard settings for this package.

    Args:
        verbose:
            If set to `True`, will cause the logger to print `logging.DEBUG` messages.
            (By default, it only prints messages with a level of `logging.INFO` and up).
    """
    handler = RichHandler(
        omit_repeated_times=False,
        show_level=False,
        show_path=False,
        markup=True,
        rich_tracebacks=True,
    )
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[handler],
    )
    return logging.getLogger(__package__)


def get_relevant_file_paths(
    raw_paths: Iterable[str],
    *allowed_exts: str,
    parent_dir: Path | None = None,
    log: Callable[[str], None] = print,
) -> list[Path]:
    """Returns a sorted list of paths for relevant files, based on the specified params.

    A "relevant" file is one that is in the sub-path of `parent_dir` (or the current
    working directory, if `parent_dir` was not provided). If any `allowed_exts` were
    provided, the file must also match one of them in order to be considered relevant.

    Each `Path` in the list returned by this function will be relative to `parent_dir`
    (or the current working directory, if `parent_dir` was not provided).

    Args:
        raw_paths:
            Strings representing file and/or directory paths that may be included
            in the resulting list, if they're deemed relevant.
            Directory paths will be recursively searched for relevant files to include.
            If omitted, the current working directory will be searched.
        *allowed_exts:
            Strings representing the file extensions to match (case-insensitive).
            If omitted, **all** file extensions will be considered relevant.
        parent_dir:
            The path to the directory that acts as a scope to determine which files are
            relevant. If omitted, the current working directory will serve as the scope.
        log:
            A function that accepts a string to be logged/printed.
            If omitted, the built-in `print` function will be used.

    Raises:
        FileNotFoundError: If `parent_dir` or any of the `raw_paths` does not
            point to an existing file/directory.
    """
    cwd = Path.cwd()
    parent_dir = (parent_dir or cwd).resolve(strict=True)
    file_paths: set[Path] = set()

    all_exts = (".*",)
    allowed_exts = tuple(f".{ext}".lower() for ext in allowed_exts) or all_exts
    exts_text = "|".join(f"[cyan]{ext.strip('.')}[/]" for ext in allowed_exts)

    for raw_path in raw_paths or ["."]:
        path = Path(raw_path).resolve(strict=True)
        if path.is_dir():
            label = "current" if (path == cwd) else f"[cyan]{get_display_path(path)}[/]"
            log(f"Searching for ({exts_text}) files inside the {label} directory.")
            for ext in allowed_exts:
                file_paths.update(path.rglob(f"*{ext}"))
        elif (allowed_exts == all_exts) or (path.suffix.lower() in allowed_exts):
            file_paths.add(path)
        else:
            log(f"Skipping [cyan]{raw_path}[/] because it isn't a ({exts_text}) file.")

    return [
        file_path.relative_to(parent_dir)
        for file_path in sorted(file_paths)
        if file_path.is_relative_to(parent_dir)
    ]
