import re


_REPEATED_PUNCTUATION_PATTERN = re.compile(r"([!?,.])\1+")
_EXTRA_SPACES_PATTERN = re.compile(r"[ \t]+")
_TRAILING_WHITESPACE_PATTERN = re.compile(r"[ \t]+(?=\n|$)")
_BLANK_LINES_PATTERN = re.compile(r"\n{3,}")
_ZERO_WIDTH_CHARS_PATTERN = re.compile("[\u200b\u200c\u200d\ufeff\u2060]")


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


def remove_trailing_whitespace(text: str) -> str:
    return _TRAILING_WHITESPACE_PATTERN.sub("", text)


def remove_zero_width_chars(text: str) -> str:
    return _ZERO_WIDTH_CHARS_PATTERN.sub("", text)


def collapse_blank_lines(text: str) -> str:
    return _BLANK_LINES_PATTERN.sub("\n\n", text)
