import os

import pytest

from ant31box.config import DefaultConfig, config
from ant31box.server.server import serve

LOCAL_DIR = os.path.dirname(__file__)


@pytest.fixture
def app():
    # Load config explicitly for the test app
    conf = config("tests/data/test_config.yaml", reload=True)
    app = serve(conf)
    return app


@pytest.fixture(autouse=True)
def reset_config():
    """
    This fixture re-initializes the global config singleton for each test.
    It is now primarily for backward compatibility tests.
    New tests should use dependency injection.
    """
    config(reload=True)


@pytest.fixture
def test_config() -> DefaultConfig:
    """Provides a test-specific configuration object via dependency injection."""
    return config("tests/data/test_config.yaml", reload=True)
