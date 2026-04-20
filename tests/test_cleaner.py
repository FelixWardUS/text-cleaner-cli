from text_cleaner_cli.cleaner import CleanerConfig, clean_text


def test_clean_text_applies_all_rules_in_fixed_order():
    raw = "  Hello!!!\r\n\r\n\r\nWorld...\t\t"
    assert clean_text(raw, CleanerConfig()) == "Hello!\n\nWorld."


def test_clean_text_can_disable_individual_rules():
    raw = "  Hello!!!\r\n\r\n\r\nWorld...\t\t"
    config = CleanerConfig(
        normalize_line_endings=False,
        zero_width_chars=True,
        trailing_whitespace=True,
        punctuation_mode="off",
        extra_spaces=True,
        blank_lines=False,
    )
    assert clean_text(raw, config) == "Hello!!!\r\n\r\n\r\nWorld..."


def test_clean_text_uses_strict_punctuation_mode_when_requested():
    assert clean_text("What?!?!", CleanerConfig(punctuation_mode="strict")) == "What?!"


def test_clean_text_preserves_markdown_fenced_code_blocks_by_default():
    raw = (
        "Intro!!!  \n"
        "```python  \n"
        "value   =   \"x!!!\"\u200b  \n"
        "\n\n"
        "```  \n"
        "Outro!!!  \n"
    )

    assert clean_text(raw, CleanerConfig()) == (
        "Intro!\n"
        "```python  \n"
        "value   =   \"x!!!\"\u200b  \n"
        "\n\n"
        "```  \n"
        "Outro!\n"
    )


def test_clean_text_can_clean_inside_markdown_fenced_code_blocks_when_disabled():
    raw = "```python\nvalue   =   \"x!!!\"\u200b  \n```\n"

    assert clean_text(raw, CleanerConfig(preserve_markdown_code_blocks=False)) == "```python\nvalue = \"x!\"\n```\n"


def test_clean_text_removes_zero_width_chars_and_trailing_whitespace_by_default():
    raw = "alpha\u200b  \nbeta\u2060\t\n"
    assert clean_text(raw, CleanerConfig(extra_spaces=False)) == "alpha\nbeta\n"


def test_clean_text_normalizes_unicode_and_typography_by_default():
    raw = "\u201cCafe\u0301\u201d\u2026"
    assert clean_text(raw, CleanerConfig()) == "\"Caf\u00e9\"."


def test_clean_text_trims_whitespace_before_collapsing_blank_lines():
    raw = "one\n   \n\t \nthree"
    assert clean_text(raw, CleanerConfig()) == "one\n\nthree"
