from functools import cache

# Achemy is an optional dependency, so we handle the import gracefully.
try:
    from achemy import AchemyEngine
except ImportError:
    AchemyEngine = None  # type: ignore

from ant31box.config import config


@cache
def get_engine() -> "AchemyEngine":
    """
    Get a cached instance of the AchemyEngine.

    This function initializes the database engine using the application's
    global configuration. It's designed to be called throughout the application
    wherever a database engine instance is needed. The `@cache` decorator
    ensures that the engine is created only once.

    Raises:
        ImportError: If the 'achemy' library is not installed.

    Returns:
        The singleton AchemyEngine instance.
    """
    if AchemyEngine is None:
        raise ImportError("The 'achemy' package is required for database functionality. Please install it.")
    return AchemyEngine(config().database)
