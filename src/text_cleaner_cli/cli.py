import argparse
import fnmatch
import sys
from glob import glob, has_magic
from pathlib import Path
from typing import Sequence, TextIO

from text_cleaner_cli.cleaner import CleanerConfig, clean_text


NO_INPUT_MESSAGE = "No input provided. Pipe text to stdin or pass one or more file paths."
PRESET_CONFIGS = {
    "minimal": {
        "unicode_form": "NFC",
        "typography": False,
        "zero_width_chars": True,
        "trailing_whitespace": True,
        "punctuation_mode": "off",
        "extra_spaces": False,
        "blank_lines": True,
    },
    "normal": {
        "unicode_form": "NFC",
        "typography": True,
        "zero_width_chars": True,
        "trailing_whitespace": True,
        "punctuation_mode": "loose",
        "extra_spaces": True,
        "blank_lines": True,
    },
    "aggressive": {
        "unicode_form": "NFKC",
        "typography": True,
        "zero_width_chars": True,
        "trailing_whitespace": True,
        "punctuation_mode": "strict",
        "extra_spaces": True,
        "blank_lines": True,
    },
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="text-cleaner")
    parser.add_argument("paths", nargs="*")
    parser.add_argument("--preset", choices=tuple(PRESET_CONFIGS), default="normal")
    parser.add_argument("--unicode-form", choices=("none", "NFC", "NFD", "NFKC", "NFKD"))
    punctuation_group = parser.add_mutually_exclusive_group()
    punctuation_group.add_argument("--punctuation-mode", choices=("loose", "strict", "off"))
    punctuation_group.add_argument(
        "--no-repeated-punctuation",
        dest="punctuation_mode",
        action="store_const",
        const="off",
    )
    parser.add_argument("--no-normalize-line-endings", action="store_true")
    parser.add_argument("--no-typography", action="store_true")
    parser.add_argument("--keep-zero-width-chars", action="store_true")
    parser.add_argument("--keep-trailing-whitespace", action="store_true")
    parser.add_argument("--clean-code-blocks", action="store_true")
    parser.add_argument("--include", action="append", default=[])
    parser.add_argument("--exclude", action="append", default=[])
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
    config = _build_config(args)

    if args.paths:
        return _process_files(args.paths, config, stdout, stderr, args.include, args.exclude)

    if stdin.isatty():
        stderr.write(f"{NO_INPUT_MESSAGE}\n")
        return 1

    stdout.write(clean_text(stdin.read(), config))
    return 0


def _build_config(args: argparse.Namespace) -> CleanerConfig:
    preset = PRESET_CONFIGS[args.preset]
    unicode_form = args.unicode_form if args.unicode_form is not None else preset["unicode_form"]
    if unicode_form == "none":
        unicode_form = None

    if args.punctuation_mode is not None:
        punctuation_mode = args.punctuation_mode
    else:
        punctuation_mode = preset["punctuation_mode"]

    return CleanerConfig(
        normalize_line_endings=not args.no_normalize_line_endings,
        preserve_markdown_code_blocks=not args.clean_code_blocks,
        unicode_form=unicode_form,
        typography=preset["typography"] and not args.no_typography,
        zero_width_chars=preset["zero_width_chars"] and not args.keep_zero_width_chars,
        trailing_whitespace=preset["trailing_whitespace"] and not args.keep_trailing_whitespace,
        punctuation_mode=punctuation_mode,
        extra_spaces=preset["extra_spaces"] and not args.no_extra_spaces,
        blank_lines=preset["blank_lines"] and not args.no_blank_lines,
    )


def _process_files(
    paths: Sequence[str],
    config: CleanerConfig,
    stdout: TextIO,
    stderr: TextIO,
    include_patterns: Sequence[str],
    exclude_patterns: Sequence[str],
) -> int:
    files = _filter_files(_expand_input_paths(paths), include_patterns, exclude_patterns)
    multiple = len(files) > 1
    succeeded = 0
    failed = 0
    changed = 0
    written_blocks = 0

    for path in files:
        try:
            raw_text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            stderr.write(f"Failed to read file: {path}\n")
            failed += 1
            if not multiple:
                return 1
            continue

        cleaned = clean_text(raw_text, config)
        succeeded += 1
        if cleaned != raw_text:
            changed += 1

        if multiple:
            if written_blocks > 0:
                stdout.write("\n")
            stdout.write(f"==> {path.name} <==\n")
            stdout.write(cleaned)
            if not cleaned.endswith("\n"):
                stdout.write("\n")
            written_blocks += 1
        else:
            stdout.write(cleaned)

    if multiple:
        stderr.write(
            f"Processed {len(files)} files: {succeeded} succeeded, {failed} failed, {changed} changed.\n"
        )
    return 1 if failed else 0


def _expand_input_paths(paths: Sequence[str]) -> list[Path]:
    files = []
    for raw_path in paths:
        if has_magic(raw_path):
            expanded_paths = [Path(match) for match in sorted(glob(raw_path, recursive=True))]
        else:
            expanded_paths = []
        if not expanded_paths:
            expanded_paths = [Path(raw_path)]
        for path in expanded_paths:
            files.extend(_expand_path(path))
    return files


def _expand_path(path: Path) -> list[Path]:
    if path.is_dir():
        return sorted(item for item in path.rglob("*") if item.is_file())
    return [path]


def _filter_files(
    files: Sequence[Path],
    include_patterns: Sequence[str],
    exclude_patterns: Sequence[str],
) -> list[Path]:
    return [
        path
        for path in files
        if _matches_include(path, include_patterns) and not _matches_any_pattern(path, exclude_patterns)
    ]


def _matches_include(path: Path, include_patterns: Sequence[str]) -> bool:
    if not include_patterns:
        return True
    return _matches_any_pattern(path, include_patterns)


def _matches_any_pattern(path: Path, patterns: Sequence[str]) -> bool:
    return any(_matches_pattern(path, pattern) for pattern in patterns)


def _matches_pattern(path: Path, pattern: str) -> bool:
    candidates = [path.name, path.as_posix()]
    try:
        candidates.append(path.resolve().relative_to(Path.cwd().resolve()).as_posix())
    except ValueError:
        pass
    return any(fnmatch.fnmatch(candidate, pattern) for candidate in candidates)
