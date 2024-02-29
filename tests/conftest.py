import os

import pytest

from ant31box.config import config

LOCAL_DIR = os.path.dirname(__file__)


@pytest.fixture
def app():
    from ant31box.server.server import serve

    app = serve()
    return app


@pytest.fixture(autouse=True)
def reset_config():
    config(reload=True)
