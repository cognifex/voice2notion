from cursor_tool import __main__


def test_run_invoked(monkeypatch):
    called = {}

    def fake_run(*, verbose=False):
        called["run"] = verbose

    monkeypatch.setattr(__main__, "run", fake_run)
    __main__.main([])
    assert called["run"] is False


def test_configure_invoked(monkeypatch):
    called = {}

    def fake_configure():
        called["config"] = True

    monkeypatch.setattr(__main__, "configure", fake_configure)
    __main__.main(["--configure"])
    assert called["config"]


def test_verbose_flag(monkeypatch):
    called = {}

    def fake_run(*, verbose=False):
        called["verbose"] = verbose

    monkeypatch.setattr(__main__, "run", fake_run)
    __main__.main(["--verbose"])
    assert called["verbose"] is True
