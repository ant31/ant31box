import platform

from ant31box.version import VERSION, Version


def test_setversion():
    Version.set_version("1.2.3")
    assert VERSION.app_version == "1.2.3"


def test_version_str():
    Version.set_version("1.2.3")
    assert str(VERSION).startswith("Running 1.2.3, with CPython")


def test_version_dict():
    Version.set_version("1.2.3")
    d = VERSION.to_dict()
    assert d["version"] == "1.2.3"
    assert "sha" in d
    assert "python" in d
    assert "system" in d
    assert "version" in d["python"]
    assert "implementation" in d["python"]
