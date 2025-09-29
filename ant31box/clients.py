import warnings
from functools import cache

from ant31box.client.filedl import DownloadClient
from ant31box.config import Config, S3ConfigSchema, config


@cache
def filedl_client(key: str = "", conf: Config | None = None) -> DownloadClient:
    """
    Create a DownloadClient instance.

    Args:
        key: A caching key. This parameter is deprecated.
        conf: A configuration object. If provided, S3 settings are initialized from it.
              If None, the global singleton is used (deprecated).

    Returns:
        A DownloadClient instance.
    """
    if key:
        warnings.warn("The 'key' parameter is deprecated and has no effect.", DeprecationWarning, stacklevel=2)

    s3_conf: S3ConfigSchema | None = None
    if conf is None:
        # Backward compatibility: use the global config if no specific config is provided.
        # This is deprecated.
        conf = config()
    if hasattr(conf.conf, "s3"):
        s3_conf = conf.conf.s3

    return DownloadClient(s3_config=s3_conf)
