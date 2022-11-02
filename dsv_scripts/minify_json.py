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
    bytes_saved, files_written, warnings = 0, 0, 0

    no_highlight = {"highlighter": None}
    log = partial(args.logger.info, extra=no_highlight)
    logd = partial(args.logger.debug, extra=no_highlight)

    for input_file, output_file in args.files:
        input_text = input_file.read_text()
        output_file_display_path = utils.get_display_path(output_file)

        if should_copy := args.should_copy(input_file):
            output_text = input_text
        else:
            minified_json = json.dumps(
                pyjson5.loads(input_text), ensure_ascii=False, separators=(",", ":")
            )
            output_text = f"{minified_json.strip()}\n"

        if output_file.exists() and (output_file.read_text() == output_text):
            logd(f"[bright_black]No change: {output_file_display_path}")
        elif should_copy:
            log(f"[bright_magenta]>>Copying:[/] {output_file_display_path}")
            output_file.write_text(input_text, newline="\n")
            files_written += 1
        else:
            log(f"[bright_yellow]Minifying:[/] {output_file_display_path}")
            output_file.write_text(output_text, newline="\n")

            input_size = input_file.stat().st_size
            output_size = output_file.stat().st_size
            size_diff = input_size - output_size

            if size_diff < 0:
                args.logger.warning(
                    f"[bright_red]  WARNING: Minified file is[/] [bright_white on red]"
                    f"{size(-size_diff)}[/] [bright_red]larger than the original file.",
                    extra=no_highlight,
                )
                warnings -= 1
            else:
                utils.print_compressed_file_info(logd, input_size, output_size)

            bytes_saved += size_diff
            files_written += 1

    utils.print_compression_task_result(log, size, bytes_saved, files_written, warnings)
    return warnings or files_written


if __name__ == "__main__":
    raise SystemExit(main())
