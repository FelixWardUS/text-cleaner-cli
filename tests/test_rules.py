from text_cleaner_cli.rules import (
    collapse_blank_lines,
    collapse_repeated_punctuation,
    normalize_typography,
    normalize_unicode,
    normalize_line_endings,
    remove_trailing_whitespace,
    remove_extra_spaces,
    remove_zero_width_chars,
)


def test_normalize_line_endings_converts_windows_and_classic_mac():
    assert normalize_line_endings("a\r\nb\rc") == "a\nb\nc"


def test_normalize_unicode_applies_requested_form():
    assert normalize_unicode("Cafe\u0301", "NFC") == "Caf\u00e9"
    assert normalize_unicode("\uff21\uff22\uff23", "NFKC") == "ABC"


def test_normalize_typography_converts_common_marks_to_ascii():
    raw = "\u201cHello\u201d \u2014 \u2018world\u2019\u2026"
    assert normalize_typography(raw) == "\"Hello\" - 'world'..."


def test_collapse_repeated_punctuation_reduces_supported_characters():
    assert collapse_repeated_punctuation("Hi!!! Wait..... Really??? No,,,") == "Hi! Wait. Really? No,"


def test_collapse_repeated_punctuation_leaves_mixed_sequences_unchanged():
    assert collapse_repeated_punctuation("What?!?!") == "What?!?!"


def test_collapse_repeated_punctuation_can_be_disabled():
    assert collapse_repeated_punctuation("Hi!!! Wait.....", mode="off") == "Hi!!! Wait....."


def test_collapse_repeated_punctuation_strict_reduces_mixed_question_exclamation_runs():
    assert collapse_repeated_punctuation("What?!?! No!?!? Stop!!!", mode="strict") == "What?! No!? Stop!"


def test_collapse_repeated_punctuation_rejects_unknown_mode():
    try:
        collapse_repeated_punctuation("Hi!!!", mode="unknown")
    except ValueError as error:
        assert str(error) == "Unsupported punctuation mode: unknown"
    else:
        raise AssertionError("Expected ValueError")


def test_remove_extra_spaces_trims_lines_and_collapses_internal_whitespace():
    assert remove_extra_spaces("  hello   world  \n\ta\t\tb\t") == "hello world\na b"


def test_remove_trailing_whitespace_preserves_leading_indentation():
    assert remove_trailing_whitespace("  indented  \n\tkept\t\nplain") == "  indented\n\tkept\nplain"


def test_remove_zero_width_chars_removes_common_invisible_codepoints():
    raw = "a\u200bb\u200cc\u200dd\ufeffe\u2060f"
    assert remove_zero_width_chars(raw) == "abcdef"


def test_collapse_blank_lines_reduces_runs_to_single_blank_line():
    assert collapse_blank_lines("one\n\n\n\n two\n\n\nthree") == "one\n\n two\n\nthree"
