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
