import json
from collections.abc import Sequence
from functools import partial

import humanize
import pyjson5

from dsv_scripts import utils
from dsv_scripts.fileio import FileIOParser


def main(argv: Sequence[str] | None = None) -> int:
    """Saves minified copies of JSON/JSON5 files."""
    parser = FileIOParser(__file__, "json", "json5", description=main.__doc__)
    args = parser.parse_args(argv)
    size = partial(humanize.naturalsize, binary=True)
    bytes_saved, files_changed, warnings = 0, 0, 0

    no_highlight = {"highlighter": None}
    log = partial(args.logger.info, extra=no_highlight)
    logd = partial(args.logger.debug, extra=no_highlight)

    for input_file, output_file in args.files:
        input_text = input_file.read_text()
        output_file_display_path = utils.get_display_path(output_file)

        if should_copy := args.should_copy(input_file):
            output_text = input_text
        else:
            output_text = json.dumps(
                pyjson5.loads(input_text), ensure_ascii=False, separators=(",", ":")
            )

        if output_file.exists() and (output_file.read_text() == output_text):
            logd(f"[bright_black]No change: {output_file_display_path}")
        elif should_copy:
            log(f"[bright_magenta]>>Copying:[/] {output_file_display_path}")
            output_file.write_text(input_text, newline="\n")
        else:
            log(f"[bright_yellow]Minifying:[/] {output_file_display_path}")
            output_file.write_text(output_text)  # No newlines written, not even at EOF.

            input_size = input_file.stat().st_size
            output_size = output_file.stat().st_size
            size_diff = input_size - output_size

            if size_diff < 0:
                args.logger.warning(
                    f"[bright_red]  WARNING: Minified file is[/] "
                    f"[bright_white on red]{size(-size_diff)}[/] "
                    f"[bright_red]larger than the original file.",
                    extra=no_highlight,
                )
                warnings -= 1
            else:
                logd(f"[red]   Before: [bright_white on red]{input_size}[/] [red]bytes")
                after_color = "green" if (size_diff > 0) else "yellow"
                logd(
                    f"[{after_color}]    After: [bright_white on {after_color}]"
                    f"{output_size}[/] [after_color]bytes"
                )

            bytes_saved += size_diff
            files_changed += 1

    log(
        f"[bright_{'red' if warnings else 'green'}]Minification complete"
        f"{f' with {-warnings} warning(s)' if warnings else ''}.[/]"
        f"{'' if files_changed else ' (All files were already up-to-date.)'}"
    )

    if files_changed:
        log(
            f"Processed [bright_white on cyan]{files_changed} file"
            f"{'s' if (files_changed > 1) else ''}[/], saving a total of [bright_white"
            f" on {'green' if (bytes_saved > 0) else 'red'}]{size(bytes_saved)}[/]."
        )

    return warnings or files_changed


if __name__ == "__main__":
    raise SystemExit(main())
