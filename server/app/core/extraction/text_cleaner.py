"""
Text cleaner — post-processing cleanup applied to all extracted text.

Handles: Unicode normalization, whitespace collapse, OCR artifact removal,
encoding fix-ups, and bullet point normalization.

Applied to both Docling (PDF) and VLM (Image) extraction outputs.
"""

import re
import unicodedata


def clean_text(text: str) -> str:
    """Apply all cleaning transformations to extracted text."""
    if not text:
        return ""

    text = _normalize_unicode(text)
    text = _fix_encoding_artifacts(text)
    text = _normalize_bullets(text)
    text = _collapse_whitespace(text)
    text = _strip_control_chars(text)

    return text.strip()


def _normalize_unicode(text: str) -> str:
    """Normalize Unicode to NFC form (composed characters)."""
    return unicodedata.normalize("NFC", text)


def _fix_encoding_artifacts(text: str) -> str:
    """Fix common encoding issues from PDF extraction."""
    replacements = {
        "\u2019": "'",     # Right single quote → apostrophe
        "\u2018": "'",     # Left single quote → apostrophe
        "\u201c": '"',     # Left double quote
        "\u201d": '"',     # Right double quote
        "\u2013": "-",     # En dash
        "\u2014": "-",     # Em dash
        "\u2026": "...",   # Ellipsis
        "\ufb01": "fi",    # fi ligature
        "\ufb02": "fl",    # fl ligature
        "\ufb03": "ffi",   # ffi ligature
        "\ufb04": "ffl",   # ffl ligature
        "\xa0": " ",       # Non-breaking space
        "\u200b": "",      # Zero-width space
        "\u200c": "",      # Zero-width non-joiner
        "\u200d": "",      # Zero-width joiner
        "\ufeff": "",      # BOM
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def _normalize_bullets(text: str) -> str:
    """Normalize various bullet point characters to a standard dash."""
    bullet_chars = [
        "\u2022",  # •
        "\u2023",  # ‣
        "\u25e6",  # ◦
        "\u2043",  # ⁃
        "\u25aa",  # ▪
        "\u25ab",  # ▫
        "\u25cf",  # ●
        "\u25cb",  # ○
        "\u27a2",  # ➢
    ]
    for char in bullet_chars:
        text = text.replace(char, "-")
    return text


def _collapse_whitespace(text: str) -> str:
    """Collapse multiple spaces/tabs into single space, preserve newlines."""
    # Collapse horizontal whitespace
    text = re.sub(r"[ \t]+", " ", text)
    # Collapse 3+ newlines to 2
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def _strip_control_chars(text: str) -> str:
    """Remove control characters except newline, tab, carriage return."""
    return "".join(
        ch for ch in text
        if ch in ("\n", "\t", "\r") or not unicodedata.category(ch).startswith("C")
    )
