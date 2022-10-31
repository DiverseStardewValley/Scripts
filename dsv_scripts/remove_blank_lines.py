import re
from collections.abc import Sequence

from dsv_scripts import utils
from dsv_scripts.fileio import FileIOParser


def main(argv: Sequence[str] | None = None) -> int:
    """Removes blank lines in text-based files."""
    args = FileIOParser(
        __file__,
        add_copy_option=False,
        description=main.__doc__,
    ).parse_args(argv)
    blank_line_regex = re.compile("\n\n")
    files_changed = 0

    for input_file, output_file in args.files:
        output_text = blank_line_regex.sub("\n", input_file.read_text())
        output_file_display_path = utils.get_display_path(output_file)

        if output_file.exists() and (output_file.read_text() == output_text):
            args.logger.debug(f"[bright_black]No change: {output_file_display_path}")
        else:
            args.logger.info(
                f"[bright_yellow]Removing blank lines in:[/] {output_file_display_path}"
            )
            output_file.write_text(output_text, newline="\n")
            files_changed += 1

    if files_changed:
        task_summary = f"Removed blank lines in {files_changed} file"
        task_summary += "s." if (files_changed > 1) else "."
    else:
        task_summary = "(All files were already up-to-date.)"

    args.logger.info(f"[bright_green]Task complete.[/] {task_summary}")
    return files_changed


if __name__ == "__main__":
    raise SystemExit(main())
