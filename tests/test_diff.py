import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from cursor_tool.diff import merge_overlaps


def test_merge_overlaps_removes_duplicate_tokens():
    assert merge_overlaps("hello world", "world again") == "hello world again"
    assert merge_overlaps("", "hi there") == "hi there"
