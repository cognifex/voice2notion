import types

from cursor_tool.typer import insert_text


def test_insert_text_uses_keyboard_write(monkeypatch):
    stub = types.SimpleNamespace(write=lambda text: stub.calls.append(text))
    stub.calls = []  # type: ignore[attr-defined]
    import cursor_tool.typer as typer

    monkeypatch.setattr(typer, "keyboard", stub, raising=False)
    monkeypatch.setattr(typer, "is_text_field_focused", lambda: True, raising=False)
    insert_text("hello")
    assert stub.calls == ["hello"]


def test_insert_text_skips_when_no_focus(monkeypatch):
    stub = types.SimpleNamespace(write=lambda text: stub.calls.append(text))
    stub.calls = []  # type: ignore[attr-defined]
    import cursor_tool.typer as typer

    monkeypatch.setattr(typer, "keyboard", stub, raising=False)
    monkeypatch.setattr(typer, "is_text_field_focused", lambda: False, raising=False)
    insert_text("ignored")
    assert stub.calls == []
