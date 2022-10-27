"""This module contains general utility functions used by multiple DSV scripts."""
from __future__ import annotations

from argparse import ArgumentParser
from collections.abc import Iterable
from pathlib import Path
from typing import Any


def get_arg_parser(description: str = "") -> ArgumentParser:
    """Creates and returns an `ArgumentParser` for a typical DSV input/output script.

    Args:
        description:
            A string containing a short, human-readable summary of what the script does.
            Will be displayed when `--help` or `-h` is specified on the command line.

    Raises:
        N/A
    """
    parser = ArgumentParser(description=description or None, add_help=False)

    def add_option(option_name: str, **kwargs: Any) -> None:
        parser.add_argument(f"-{option_name[0]}", f"--{option_name}", **kwargs)

    for name, var in [("input", "X"), ("output", "Y")]:
        add_option(name, default=".", help=f"name of the {name} directory", metavar=var)

    add_option("force", action="store_true", help="force execute (may overwrite files)")
    add_option("verbose", action="store_true", help="enable verbose console output")
    add_option("help", action="help", help="show this help message")

    return parser


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
        print(
            f"Input and output directories are the same: {input_dir_path}\n"
            "Exiting to avoid overwriting files (use '-f' to bypass this check)."
        )
        raise SystemExit(1)

    return input_dir_path, output_dir_path


def get_relevant_file_paths(
    raw_paths: Iterable[str],
    *allowed_exts: str,
    parent_dir: Path | None = None,
    verbose: bool = False,
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
        *allowed_exts:
            Strings representing the file extensions to match (case-insensitive).
            If omitted, **all** file extensions will be considered relevant.
        parent_dir:
            The path to the directory that acts as a scope to determine which files are
            relevant. If omitted, the current working directory will serve as the scope.
        verbose:
            If set to `True`, will print information about excluded files/directories.

    Raises:
        FileNotFoundError: If `parent_dir` or any of the `raw_paths` does not
            point to an existing file/directory.
    """
    all_exts = ("*",)
    allowed_exts = tuple(ext.strip(".").lower() for ext in allowed_exts) or all_exts
    parent_dir = (parent_dir or Path.cwd()).resolve(strict=True)
    file_paths: set[Path] = set()

    def populate_file_paths(source_path: Path) -> None:
        if source_path.is_dir():
            for ext in allowed_exts:
                file_paths.update(source_path.rglob(f"*.{ext}"))
        elif (allowed_exts == all_exts) or (source_path.suffix.lower() in allowed_exts):
            file_paths.add(source_path)
        elif verbose:
            print(f"Path '{source_path}' has an irrelevant file extension. Ignoring.")

    for raw_path in raw_paths:
        path = Path(raw_path).resolve(strict=True)
        if path.is_relative_to(parent_dir):
            populate_file_paths(path)
        elif verbose:
            print(f"Path '{path}' is not in the relevant directory. Ignoring.")

    return [file_path.relative_to(parent_dir) for file_path in sorted(file_paths)]
