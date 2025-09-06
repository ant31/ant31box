import os

import pytest

from ant31box.config import config
from ant31box.server.server import serve

LOCAL_DIR = os.path.dirname(__file__)


@pytest.fixture
def app():
    app = serve()
    return app


@pytest.fixture(autouse=True)
def reset_config():
    config(reload=True)
