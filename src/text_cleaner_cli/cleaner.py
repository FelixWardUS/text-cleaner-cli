import re
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


_FENCE_START_PATTERN = re.compile(r"^[ \t]{0,3}(`{3,}|~{3,})")


@dataclass(slots=True)
class CleanerConfig:
    normalize_line_endings: bool = True
    preserve_markdown_code_blocks: bool = True
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
    if config.preserve_markdown_code_blocks:
        return _clean_preserving_markdown_code_blocks(cleaned, config)
    return _clean_text_segment(cleaned, config)


def _clean_text_segment(text: str, config: CleanerConfig) -> str:
    cleaned = text
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


def _clean_preserving_markdown_code_blocks(text: str, config: CleanerConfig) -> str:
    parts = []
    outside_lines = []
    code_lines = []
    fence_char = ""
    fence_length = 0

    for line in text.splitlines(keepends=True):
        if code_lines:
            code_lines.append(line)
            if _is_fence_end(line, fence_char, fence_length):
                parts.append("".join(code_lines))
                code_lines = []
                fence_char = ""
                fence_length = 0
            continue

        fence = _get_fence_start(line)
        if fence:
            if outside_lines:
                parts.append(_clean_text_segment("".join(outside_lines), config))
                outside_lines = []
            fence_char, fence_length = fence
            code_lines.append(line)
            continue

        outside_lines.append(line)

    if outside_lines:
        parts.append(_clean_text_segment("".join(outside_lines), config))
    if code_lines:
        parts.append("".join(code_lines))
    return "".join(parts)


def _get_fence_start(line: str) -> tuple[str, int] | None:
    match = _FENCE_START_PATTERN.match(line)
    if not match:
        return None
    marker = match.group(1)
    return marker[0], len(marker)


def _is_fence_end(line: str, fence_char: str, fence_length: int) -> bool:
    stripped = line.strip(" \t\n")
    return len(stripped) >= fence_length and set(stripped) == {fence_char}
