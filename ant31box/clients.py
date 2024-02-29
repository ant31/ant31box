from functools import cache

from ant31box.client.filedl import DownloadClient


@cache
def filedl_client(key: str = "") -> DownloadClient:
    """
    Create a EPostClient instance with the given key
    It cache the answer for the same key
    use filedl_client.cache_clear() to clear the cache
    """
    _ = key
    return DownloadClient()
