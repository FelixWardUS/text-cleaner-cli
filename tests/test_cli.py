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


def test_main_supports_strict_punctuation_mode():
    stdin = StringIO("What?!?!\n")
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["--punctuation-mode", "strict"], stdin=stdin, stdout=stdout, stderr=stderr)

    assert exit_code == 0
    assert stdout.getvalue() == "What?!\n"
    assert stderr.getvalue() == ""


def test_main_supports_aggressive_preset():
    stdin = StringIO("\uff21\u2014What?!?!\n")
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["--preset", "aggressive"], stdin=stdin, stdout=stdout, stderr=stderr)

    assert exit_code == 0
    assert stdout.getvalue() == "A-What?!\n"
    assert stderr.getvalue() == ""


def test_main_supports_minimal_preset():
    stdin = StringIO("  Hi!!!   there\u2014  \n\n\n")
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["--preset", "minimal"], stdin=stdin, stdout=stdout, stderr=stderr)

    assert exit_code == 0
    assert stdout.getvalue() == "  Hi!!!   there\u2014\n\n"
    assert stderr.getvalue() == ""


def test_main_supports_unicode_form_override():
    stdin = StringIO("\uff21\uff22\uff23\n")
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["--unicode-form", "NFKC"], stdin=stdin, stdout=stdout, stderr=stderr)

    assert exit_code == 0
    assert stdout.getvalue() == "ABC\n"
    assert stderr.getvalue() == ""


def test_main_can_keep_zero_width_chars_and_trailing_whitespace():
    stdin = StringIO("a\u200b  \n")
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(
        ["--keep-zero-width-chars", "--keep-trailing-whitespace", "--no-extra-spaces"],
        stdin=stdin,
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 0
    assert stdout.getvalue() == "a\u200b  \n"
    assert stderr.getvalue() == ""


def test_main_can_clean_markdown_code_blocks_when_requested():
    stdin = StringIO("```python\nvalue   =   \"x!!!\"\u200b  \n```\n")
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["--clean-code-blocks"], stdin=stdin, stdout=stdout, stderr=stderr)

    assert exit_code == 0
    assert stdout.getvalue() == "```python\nvalue = \"x!\"\n```\n"
    assert stderr.getvalue() == ""


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
