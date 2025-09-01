from cursor_tool import __main__


def test_run_invoked(monkeypatch):
    called = {}

    def fake_run():
        called["run"] = True

    monkeypatch.setattr(__main__, "run", fake_run)
    __main__.main([])
    assert called["run"]


def test_configure_invoked(monkeypatch):
    called = {}

    def fake_configure():
        called["config"] = True

    monkeypatch.setattr(__main__, "configure", fake_configure)
    __main__.main(["--configure"])
    assert called["config"]
