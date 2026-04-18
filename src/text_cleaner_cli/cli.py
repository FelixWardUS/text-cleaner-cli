import argparse
import sys
from pathlib import Path
from typing import Sequence, TextIO

from text_cleaner_cli.cleaner import CleanerConfig, clean_text


NO_INPUT_MESSAGE = "No input provided. Pipe text to stdin or pass one or more file paths."


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="text-cleaner")
    parser.add_argument("paths", nargs="*")
    parser.add_argument("--no-normalize-line-endings", action="store_true")
    parser.add_argument("--no-repeated-punctuation", action="store_true")
    parser.add_argument("--no-extra-spaces", action="store_true")
    parser.add_argument("--no-blank-lines", action="store_true")
    return parser


def main(
    argv: Sequence[str] | None = None,
    *,
    stdin: TextIO | None = None,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    stdin = stdin or sys.stdin
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr
    config = CleanerConfig(
        normalize_line_endings=not args.no_normalize_line_endings,
        repeated_punctuation=not args.no_repeated_punctuation,
        extra_spaces=not args.no_extra_spaces,
        blank_lines=not args.no_blank_lines,
    )

    if args.paths:
        return _process_files(args.paths, config, stdout, stderr)

    if stdin.isatty():
        stderr.write(f"{NO_INPUT_MESSAGE}\n")
        return 1

    stdout.write(clean_text(stdin.read(), config))
    return 0


def _process_files(paths: Sequence[str], config: CleanerConfig, stdout: TextIO, stderr: TextIO) -> int:
    multiple = len(paths) > 1
    for index, raw_path in enumerate(paths):
        path = Path(raw_path)
        try:
            cleaned = clean_text(path.read_text(encoding="utf-8"), config)
        except (OSError, UnicodeDecodeError):
            stderr.write(f"Failed to read file: {raw_path}\n")
            return 1

        if multiple:
            if index > 0:
                stdout.write("\n")
            stdout.write(f"==> {path.name} <==\n")
            stdout.write(cleaned)
            if not cleaned.endswith("\n"):
                stdout.write("\n")
        else:
            stdout.write(cleaned)
    return 0
