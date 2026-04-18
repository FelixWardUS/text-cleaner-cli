# Text Cleaner CLI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Python CLI that cleans text from `stdin` or file paths, enables four cleaning rules by default, and supports `--no-*` flags to disable each rule.

**Architecture:** Use a small `src/` package. Keep pure text-cleaning rule functions in `rules.py`, pipeline orchestration in `cleaner.py`, and argument parsing plus I/O in `cli.py`. Package the CLI with a console script entry point named `text-cleaner`.

**Tech Stack:** Python 3.11+, standard library (`argparse`, `dataclasses`, `pathlib`, `re`, `sys`, `io`), `pytest`

---

## File Structure

- Create: `pyproject.toml`
- Create: `src/text_cleaner_cli/__init__.py`
- Create: `src/text_cleaner_cli/__main__.py`
- Create: `src/text_cleaner_cli/rules.py`
- Create: `src/text_cleaner_cli/cleaner.py`
- Create: `src/text_cleaner_cli/cli.py`
- Create: `tests/test_rules.py`
- Create: `tests/test_cleaner.py`
- Create: `tests/test_cli.py`
- Modify: `README.md`

### Task 1: Bootstrap Package and Rule Functions

**Files:**
- Create: `pyproject.toml`
- Create: `src/text_cleaner_cli/__init__.py`
- Create: `src/text_cleaner_cli/rules.py`
- Test: `tests/test_rules.py`

- [ ] **Step 1: Write the failing rule tests**

```python
from text_cleaner_cli.rules import (
    collapse_blank_lines,
    collapse_repeated_punctuation,
    normalize_line_endings,
    remove_extra_spaces,
)


def test_normalize_line_endings_converts_windows_and_classic_mac():
    assert normalize_line_endings("a\r\nb\rc") == "a\nb\nc"


def test_collapse_repeated_punctuation_reduces_supported_characters():
    assert collapse_repeated_punctuation("Hi!!! Wait..... Really??? No,,,") == "Hi! Wait. Really? No,"


def test_collapse_repeated_punctuation_leaves_mixed_sequences_unchanged():
    assert collapse_repeated_punctuation("What?!?!") == "What?!?!"


def test_remove_extra_spaces_trims_lines_and_collapses_internal_whitespace():
    assert remove_extra_spaces("  hello   world  \n\ta\t\tb\t") == "hello world\na b"


def test_collapse_blank_lines_reduces_runs_to_single_blank_line():
    assert collapse_blank_lines("one\n\n\n\n two\n\n\nthree") == "one\n\n two\n\nthree"
```

- [ ] **Step 2: Run the tests and verify they fail for the right reason**

Run: `pytest tests/test_rules.py -q`
Expected: FAIL with `ModuleNotFoundError` or import failure because `text_cleaner_cli.rules` does not exist yet.

- [ ] **Step 3: Write the minimal package files and rule implementations**

```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "text-cleaner-cli"
version = "0.1.0"
description = "A simple command-line tool to clean messy text."
readme = "README.md"
requires-python = ">=3.11"
license = { file = "LICENSE" }
authors = [{ name = "FelixWardUS" }]
dependencies = []

[project.optional-dependencies]
dev = ["pytest>=8.0"]

[project.scripts]
text-cleaner = "text_cleaner_cli.cli:main"

[tool.pytest.ini_options]
pythonpath = ["src"]
```

```python
__all__ = [
    "cleaner",
    "cli",
    "rules",
]
```

```python
import re


_REPEATED_PUNCTUATION_PATTERN = re.compile(r"([!?,.])\1+")
_EXTRA_SPACES_PATTERN = re.compile(r"[ \t]+")
_BLANK_LINES_PATTERN = re.compile(r"\n{3,}")


def normalize_line_endings(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def collapse_repeated_punctuation(text: str) -> str:
    return _REPEATED_PUNCTUATION_PATTERN.sub(r"\1", text)


def remove_extra_spaces(text: str) -> str:
    cleaned_lines = []
    for line in text.split("\n"):
        stripped = line.strip(" \t")
        cleaned_lines.append(_EXTRA_SPACES_PATTERN.sub(" ", stripped))
    return "\n".join(cleaned_lines)


def collapse_blank_lines(text: str) -> str:
    return _BLANK_LINES_PATTERN.sub("\n\n", text)
```

- [ ] **Step 4: Run the rule tests and verify they pass**

Run: `pytest tests/test_rules.py -q`
Expected: PASS with `5 passed`

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml src/text_cleaner_cli/__init__.py src/text_cleaner_cli/rules.py tests/test_rules.py
git commit -m "feat: add text cleaning rules"
```

### Task 2: Add the Cleaning Pipeline

**Files:**
- Create: `src/text_cleaner_cli/cleaner.py`
- Test: `tests/test_cleaner.py`

- [ ] **Step 1: Write the failing cleaner tests**

```python
from text_cleaner_cli.cleaner import CleanerConfig, clean_text


def test_clean_text_applies_all_rules_in_fixed_order():
    raw = "  Hello!!!\r\n\r\n\r\nWorld...\t\t"
    assert clean_text(raw, CleanerConfig()) == "Hello!\n\nWorld."


def test_clean_text_can_disable_individual_rules():
    raw = "  Hello!!!\r\n\r\n\r\nWorld...\t\t"
    config = CleanerConfig(
        normalize_line_endings=False,
        repeated_punctuation=False,
        extra_spaces=True,
        blank_lines=False,
    )
    assert clean_text(raw, config) == "Hello!!!\n\n\nWorld..."


def test_clean_text_trims_whitespace_before_collapsing_blank_lines():
    raw = "one\n   \n\t \nthree"
    assert clean_text(raw, CleanerConfig()) == "one\n\nthree"
```

- [ ] **Step 2: Run the tests and verify they fail**

Run: `pytest tests/test_cleaner.py -q`
Expected: FAIL because `text_cleaner_cli.cleaner` does not exist yet.

- [ ] **Step 3: Write the minimal cleaner implementation**

```python
from dataclasses import dataclass

from text_cleaner_cli.rules import (
    collapse_blank_lines,
    collapse_repeated_punctuation,
    normalize_line_endings,
    remove_extra_spaces,
)


@dataclass(slots=True)
class CleanerConfig:
    normalize_line_endings: bool = True
    repeated_punctuation: bool = True
    extra_spaces: bool = True
    blank_lines: bool = True


def clean_text(text: str, config: CleanerConfig) -> str:
    cleaned = text
    if config.normalize_line_endings:
        cleaned = normalize_line_endings(cleaned)
    if config.repeated_punctuation:
        cleaned = collapse_repeated_punctuation(cleaned)
    if config.extra_spaces:
        cleaned = remove_extra_spaces(cleaned)
    if config.blank_lines:
        cleaned = collapse_blank_lines(cleaned)
    return cleaned
```

- [ ] **Step 4: Run the cleaner tests and verify they pass**

Run: `pytest tests/test_cleaner.py -q`
Expected: PASS with `3 passed`

- [ ] **Step 5: Commit**

```bash
git add src/text_cleaner_cli/cleaner.py tests/test_cleaner.py
git commit -m "feat: add cleaning pipeline"
```

### Task 3: Build the CLI and I/O Behavior

**Files:**
- Create: `src/text_cleaner_cli/cli.py`
- Create: `src/text_cleaner_cli/__main__.py`
- Test: `tests/test_cli.py`

- [ ] **Step 1: Write the failing CLI tests**

```python
from io import StringIO
from pathlib import Path

from text_cleaner_cli.cli import main


def test_main_reads_stdin_when_no_paths_are_given():
    stdin = StringIO("  Hello!!!\n\n\nWorld...\n")
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main([], stdin=stdin, stdout=stdout, stderr=stderr)

    assert exit_code == 0
    assert stdout.getvalue() == "Hello!\n\nWorld.\n"
    assert stderr.getvalue() == ""


def test_main_reads_single_file_without_header(tmp_path: Path):
    sample = tmp_path / "sample.txt"
    sample.write_text("  Hello!!!\n", encoding="utf-8")

    stdout = StringIO()
    stderr = StringIO()

    exit_code = main([str(sample)], stdout=stdout, stderr=stderr)

    assert exit_code == 0
    assert stdout.getvalue() == "Hello!\n"
    assert stderr.getvalue() == ""


def test_main_reads_multiple_files_with_headers(tmp_path: Path):
    first = tmp_path / "first.txt"
    second = tmp_path / "second.txt"
    first.write_text("Hi!!!", encoding="utf-8")
    second.write_text("Bye...\n", encoding="utf-8")

    stdout = StringIO()
    stderr = StringIO()

    exit_code = main([str(first), str(second)], stdout=stdout, stderr=stderr)

    assert exit_code == 0
    assert stdout.getvalue() == "==> first.txt <==\nHi!\n\n==> second.txt <==\nBye.\n"
    assert stderr.getvalue() == ""


def test_main_respects_no_flags_for_individual_rules():
    stdin = StringIO("  Hello!!!\n\n\nWorld...\n")
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["--no-repeated-punctuation", "--no-blank-lines"], stdin=stdin, stdout=stdout, stderr=stderr)

    assert exit_code == 0
    assert stdout.getvalue() == "Hello!!!\n\n\nWorld...\n"


def test_main_returns_error_when_no_input_is_available():
    stdin = StringIO("")
    stdin.isatty = lambda: True
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main([], stdin=stdin, stdout=stdout, stderr=stderr)

    assert exit_code == 1
    assert stdout.getvalue() == ""
    assert stderr.getvalue() == "No input provided. Pipe text to stdin or pass one or more file paths.\n"


def test_main_reports_unreadable_file(tmp_path: Path):
    missing = tmp_path / "missing.txt"
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main([str(missing)], stdout=stdout, stderr=stderr)

    assert exit_code == 1
    assert stdout.getvalue() == ""
    assert stderr.getvalue() == f"Failed to read file: {missing}\n"
```

- [ ] **Step 2: Run the tests and verify they fail**

Run: `pytest tests/test_cli.py -q`
Expected: FAIL because `text_cleaner_cli.cli` does not exist yet.

- [ ] **Step 3: Write the minimal CLI implementation**

```python
import argparse
import sys
from pathlib import Path
from typing import Sequence, TextIO

from text_cleaner_cli.cleaner import CleanerConfig, clean_text


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
        stderr.write("No input provided. Pipe text to stdin or pass one or more file paths.\n")
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
```

```python
from text_cleaner_cli.cli import main


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run the CLI tests and verify they pass**

Run: `pytest tests/test_cli.py -q`
Expected: PASS with `6 passed`

- [ ] **Step 5: Commit**

```bash
git add src/text_cleaner_cli/cli.py src/text_cleaner_cli/__main__.py tests/test_cli.py
git commit -m "feat: add text cleaner cli"
```

### Task 4: Finalize Documentation and Full Verification

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Update README with installation, usage, and output behavior**

````markdown
# Text Cleaner CLI

A simple command-line tool to clean up messy text files and copied text snippets.

## Features
- Remove extra spaces
- Collapse repeated blank lines
- Normalize line endings
- Clean repeated punctuation

## Installation
```bash
python -m pip install -e .[dev]
```

## Usage
```bash
text-cleaner input.txt
text-cleaner file1.txt file2.txt
cat input.txt | text-cleaner
text-cleaner --no-repeated-punctuation --no-blank-lines input.txt
```

## Output

- Single input source writes cleaned text directly to `stdout`
- Multiple file inputs write a header before each cleaned file block
- The CLI does not modify files in place
````

- [ ] **Step 2: Run the full test suite and verify everything passes**

Run: `pytest -q`
Expected: PASS with all tests green and no failures

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs: document cli usage"
```

## Self-Review

- Spec coverage:
  - Inputs from `stdin` and file paths: covered by Task 3 tests and implementation
  - Default-on rules and `--no-*` flags: covered by Task 2 and Task 3
  - Multiple file separators and newline handling: covered by Task 3
  - Error handling for no input and unreadable files: covered by Task 3
  - Packaging and console entry point: covered by Task 1 and Task 3
- Placeholder scan:
  - No unresolved placeholder markers remain
  - Each task includes exact files, commands, and code snippets
- Type consistency:
  - `CleanerConfig`, `clean_text()`, and `main()` names are consistent across tasks
