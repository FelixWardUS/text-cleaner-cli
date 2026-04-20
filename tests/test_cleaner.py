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
        repeated_punctuation=False,
        extra_spaces=True,
        blank_lines=False,
    )
    assert clean_text(raw, config) == "Hello!!!\r\n\r\n\r\nWorld..."


def test_clean_text_removes_zero_width_chars_and_trailing_whitespace_by_default():
    raw = "alpha\u200b  \nbeta\u2060\t\n"
    assert clean_text(raw, CleanerConfig(extra_spaces=False)) == "alpha\nbeta\n"


def test_clean_text_trims_whitespace_before_collapsing_blank_lines():
    raw = "one\n   \n\t \nthree"
    assert clean_text(raw, CleanerConfig()) == "one\n\nthree"
