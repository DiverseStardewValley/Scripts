import os
import shutil
from collections.abc import Callable, Sequence
from functools import partial

import dotenv
import humanize
import tinify
from rich.progress import track

from dsv_scripts import utils
from dsv_scripts.fileio import FileIOParser


def main(argv: Sequence[str] | None = None) -> int:
    """Saves compressed copies of PNG images."""
    args = FileIOParser(__file__, "png", description=main.__doc__).parse_args(argv)
    files_to_write = [out_file for _, out_file in args.files if not out_file.exists()]

    if files_to_write and not setup_tinify(args.logger.info):
        return -1  # An appropriate error message will already have been printed.

    size = partial(humanize.naturalsize, binary=True)
    bytes_saved, files_written, warnings = 0, 0, 0

    no_highlight = {"highlighter": None}
    log = partial(args.logger.info, extra=no_highlight)
    logd = partial(args.logger.debug, extra=no_highlight)

    for input_file, output_file in track(args.files):
        output_file_display_path = utils.get_display_path(output_file)

        if output_file not in files_to_write:
            logd(f"[bright_black]File already exists: {output_file_display_path}")
        elif args.should_copy(input_file):
            log(f"[bright_magenta]>>Copying:[/] {output_file_display_path}")
            shutil.copy(input_file, output_file)
            files_written += 1
        else:
            log(f"[bright_yellow]Tinifying:[/] {output_file_display_path}")
            tinify.from_file(input_file).to_file(output_file)

            input_size = input_file.stat().st_size
            output_size = output_file.stat().st_size
            size_diff = input_size - output_size

            if size_diff < 0:
                args.logger.warning(
                    f"[bright_red]  WARNING: Tinified file is[/] [bright_white on red]"
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


def setup_tinify(log: Callable[[str], None]) -> bool:
    """Returns `True` if Tinify was successfully initialized, or `False` otherwise."""
    dotenv.load_dotenv(".env")
    tinify_api_key = os.environ.get("TINIFY_API_KEY")
    error_hint_text = (
        "\n\nYou can get a free API key from the TinyPNG website:\n",
        ("https://tinypng.com/developers", "bright_cyan"),
        "\n\nSave it in a file named ",
        (".env", "bright_magenta"),
        " with the following format:\n",
        ("TINIFY_API_KEY=PasteYourApiKeyHere", "bright_cyan"),
        ("\n\n!!! DO NOT COMMIT/SHARE/LEAK YOUR .env FILE !!!", "bright_yellow"),
    )

    if not tinify_api_key:
        utils.print_error(
            ("TINIFY_API_KEY environment variable not found.", "bright_red"),
            *error_hint_text,
        )
        return False

    try:
        tinify.key = tinify_api_key
        tinify.validate()
    except tinify.Error:
        utils.print_error(
            ("Validation of Tinify API key failed.", "bright_red"),
            *error_hint_text,
        )
        return False

    # This number is defined on Tinify's website and may be subject to change.
    max_compressions_per_month = 500
    # The `compression_count` property is only available after validating the API key.
    compressions_left = max(0, max_compressions_per_month - tinify.compression_count)

    if compressions_left:
        log(
            f"Successfully connected to Tinify. {compressions_left} compression"
            f"{'s' if (compressions_left > 1) else ''} remaining for this month."
        )
        return True
    else:
        utils.print_error(
            ("No more Tinify compressions remaining for this month.", "bright_yellow")
        )
        return False


if __name__ == "__main__":
    raise SystemExit(main())
