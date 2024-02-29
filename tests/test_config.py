import os

from ant31box.config import config


def test_config_test_env():
    assert config().app.env == "test"


def test_config_fields():
    assert config().sentry.dsn is None
    assert config().server.port == 8080
    assert config().logging.level == "info"
    assert config().conf.app.env == "test"


def test_config_reinit():
    conf = config().model_dump()
    _ = config(reload=True)
    assert config().model_dump() == conf
    # Changes are ignored without reinit
    config("tests/data/config-2.yaml")
    assert config().model_dump() == conf
    # Changes are applied after reinit
    config("tests/data/config-2.yaml", reload=True)
    assert config().model_dump() != conf


def test_config_path_load():
    config("tests/data/config-2.yaml", reload=True)
    assert config().app.env == "test-2"


def test_config_path_load_from_env(monkeypatch):
    monkeypatch.setattr(os, "environ", {"ANT31BOX_CONFIG": "tests/data/config-2.yaml"})
    assert config(reload=True).app.env == "test-2"


def test_config_path_failed_path_fallback():
    config("tests/data/config-dontexist.yaml", reload=True)
    assert config().app.env == "dev"
