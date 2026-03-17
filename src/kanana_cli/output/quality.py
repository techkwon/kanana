import re


_REPEATED_PUNCTUATION = re.compile(r"([!！?？~])\1+")
_MIXED_END_PUNCTUATION = re.compile(r"([.!?])(?:[!！?？~])+")
_HANGUL_DECORATION = re.compile(r"(?<=[가-힣])(?:[ \t]*[!！?？~]+[ \t]*)+(?=[가-힣])")
_SPACE_BEFORE_PUNCT = re.compile(r"\s+([,.!?])")
_SPACE_AROUND_NEWLINES = re.compile(r"[ \t]*\n[ \t]*")
_EXCESS_NEWLINES = re.compile(r"\n{3,}")


def clean_generated_text(text: str) -> str:
    normalized = text.replace("\r\n", "\n").strip()
    normalized = _REPEATED_PUNCTUATION.sub(r"\1", normalized)
    normalized = _MIXED_END_PUNCTUATION.sub(r"\1", normalized)
    normalized = _HANGUL_DECORATION.sub("", normalized)
    normalized = _SPACE_BEFORE_PUNCT.sub(r"\1", normalized)
    normalized = _SPACE_AROUND_NEWLINES.sub("\n", normalized)
    normalized = _EXCESS_NEWLINES.sub("\n\n", normalized)
    return normalized.strip()
