from dataclasses import dataclass

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


@dataclass(slots=True)
class CleanerConfig:
    normalize_line_endings: bool = True
    unicode_form: str | None = "NFC"
    typography: bool = True
    zero_width_chars: bool = True
    trailing_whitespace: bool = True
    punctuation_mode: str = "loose"
    extra_spaces: bool = True
    blank_lines: bool = True


def clean_text(text: str, config: CleanerConfig) -> str:
    cleaned = text
    if config.normalize_line_endings:
        cleaned = normalize_line_endings(cleaned)
    if config.zero_width_chars:
        cleaned = remove_zero_width_chars(cleaned)
    if config.unicode_form:
        cleaned = normalize_unicode(cleaned, config.unicode_form)
    if config.typography:
        cleaned = normalize_typography(cleaned)
    cleaned = collapse_repeated_punctuation(cleaned, mode=config.punctuation_mode)
    if config.trailing_whitespace:
        cleaned = remove_trailing_whitespace(cleaned)
    if config.extra_spaces:
        cleaned = remove_extra_spaces(cleaned)
    if config.blank_lines:
        cleaned = collapse_blank_lines(cleaned)
    return cleaned
