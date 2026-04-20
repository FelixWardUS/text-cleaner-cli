import re
import unicodedata


_REPEATED_PUNCTUATION_PATTERN = re.compile(r"([!?,.])\1+")
_QUESTION_EXCLAMATION_RUN_PATTERN = re.compile(r"[!?]{2,}")
_EXTRA_SPACES_PATTERN = re.compile(r"[ \t]+")
_TRAILING_WHITESPACE_PATTERN = re.compile(r"[ \t]+(?=\n|$)")
_BLANK_LINES_PATTERN = re.compile(r"\n{3,}")
_ZERO_WIDTH_CHARS_PATTERN = re.compile("[\u200b\u200c\u200d\ufeff\u2060]")
_TYPOGRAPHY_TRANSLATION = str.maketrans(
    {
        "\u2018": "'",
        "\u2019": "'",
        "\u201a": "'",
        "\u201b": "'",
        "\u2039": "'",
        "\u203a": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u201e": '"',
        "\u201f": '"',
        "\u00ab": '"',
        "\u00bb": '"',
        "\u2010": "-",
        "\u2011": "-",
        "\u2012": "-",
        "\u2013": "-",
        "\u2014": "-",
        "\u2015": "-",
        "\u2212": "-",
        "\u2026": "...",
    }
)


def normalize_line_endings(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def normalize_unicode(text: str, form: str | None) -> str:
    if form is None:
        return text
    return unicodedata.normalize(form, text)


def normalize_typography(text: str) -> str:
    return text.translate(_TYPOGRAPHY_TRANSLATION)


def collapse_repeated_punctuation(text: str, mode: str = "loose") -> str:
    if mode == "off":
        return text
    if mode not in {"loose", "strict"}:
        raise ValueError(f"Unsupported punctuation mode: {mode}")

    cleaned = _REPEATED_PUNCTUATION_PATTERN.sub(r"\1", text)
    if mode == "strict":
        cleaned = _QUESTION_EXCLAMATION_RUN_PATTERN.sub(_collapse_question_exclamation_run, cleaned)
    return cleaned


def _collapse_question_exclamation_run(match: re.Match[str]) -> str:
    seen = []
    for char in match.group(0):
        if char not in seen:
            seen.append(char)
    return "".join(seen)


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
