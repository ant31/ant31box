# Achemy is an optional dependency, so we handle the import gracefully.
try:
    from achemy import AchemyEngine
except ImportError:
    AchemyEngine = None  # type: ignore

from ant31box.config import Config


def get_engine(conf: Config) -> "AchemyEngine":
    """
    Get an instance of the AchemyEngine.

    This function initializes the database engine using the provided
    configuration object.

    Args:
        conf: The application configuration object.

    Raises:
        ImportError: If the 'achemy' library is not installed.

    Returns:
        An AchemyEngine instance.
    """
    if AchemyEngine is None:
        raise ImportError("The 'achemy' package is required for database functionality. Please install it.")
    return AchemyEngine(conf.database)
