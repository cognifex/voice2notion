from __future__ import annotations

"""Helpers for merging transcription chunks via simple diffs.

Currently we only expose ``merge_overlaps`` which joins two pieces of
text and removes duplicated trailing/leading words.  It operates on
whitespace separated tokens and is intentionally small so it can be
unit tested without heavy dependencies.
"""

from typing import List


def merge_overlaps(previous: str, new: str) -> str:
    """Merge ``new`` into ``previous`` by removing overlapping words.

    Parameters
    ----------
    previous:
        Text that has already been emitted.
    new:
        Text for the next chunk which may overlap with the end of
        ``previous``.

    Examples
    --------
    >>> merge_overlaps("hello world", "world again")
    'hello world again'
    """

    if not previous:
        return new
    prev_tokens: List[str] = previous.split()
    new_tokens: List[str] = new.split()
    max_overlap = min(len(prev_tokens), len(new_tokens))
    overlap = 0
    for i in range(max_overlap, 0, -1):
        if prev_tokens[-i:] == new_tokens[:i]:
            overlap = i
            break
    merged = prev_tokens + new_tokens[overlap:]
    return " ".join(merged)
