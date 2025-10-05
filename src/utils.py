"""Utility helpers shared across the PolicyBot codebase."""

from __future__ import annotations

import re
from typing import Iterable, List

__all__ = ["clean_text", "clean_corpus"]

_WHITESPACE_PATTERN = re.compile(r"\s+")


def clean_text(text: str) -> str:
    """Normalize whitespace in *text* and strip leading/trailing space.

    Parameters
    ----------
    text:
        Raw text that may include inconsistent whitespace characters.

    Returns
    -------
    str
        A single-line string with collapsed whitespace. If the input contains
        only whitespace characters, an empty string is returned.

    Raises
    ------
    TypeError
        If *text* is ``None``.
    """

    if text is None:  # pragma: no cover - defensive programming
        raise TypeError("text must be a string")

    normalized = _WHITESPACE_PATTERN.sub(" ", text).strip()
    return normalized


def clean_corpus(texts: Iterable[str]) -> List[str]:
    """Clean a collection of policy snippets and drop empty entries.

    Parameters
    ----------
    texts:
        An iterable of raw policy strings. Items are cleaned with
        :func:`clean_text`. Empty results are discarded.

    Returns
    -------
    list of str
        A list containing only non-empty, cleaned policy snippets.

    Raises
    ------
    ValueError
        If no valid policy text remains after cleaning.
    """

    cleaned: List[str] = []
    for item in texts:
        normalized = clean_text(item)
        if normalized:
            cleaned.append(normalized)

    if not cleaned:
        raise ValueError("No valid policy text provided.")

    return cleaned
