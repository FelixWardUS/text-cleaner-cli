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
