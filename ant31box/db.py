import warnings
from functools import cache

# Achemy is an optional dependency, so we handle the import gracefully.
try:
    from achemy import AchemyEngine
except ImportError:
    AchemyEngine = None  # type: ignore

from ant31box.config import Config, config


@cache
def get_engine(conf: Config | None = None) -> "AchemyEngine":
    """
    Get a cached instance of the AchemyEngine.

    This function initializes the database engine using the provided configuration
    object. For backward compatibility, it falls back to the global `config()`
    singleton if no configuration is provided.

    Args:
        conf: The application configuration object (recommended).

    Raises:
        ImportError: If the 'achemy' library is not installed.

    Returns:
        A cached AchemyEngine instance.
    """
    if AchemyEngine is None:
        raise ImportError("The 'achemy' package is required for database functionality. Please install it.")

    if conf is None:
        warnings.warn(
            "Calling get_engine() without a config object is deprecated. Please pass the configuration explicitly.",
            DeprecationWarning,
            stacklevel=2,
        )
        _conf = config()
    else:
        _conf = conf

    return AchemyEngine(_conf.database)
