import collections.abc


def deepmerge(source: dict, destination: dict) -> dict:
    """
    Deeply merges two dictionaries.

    Args:
        source: The source dictionary.
        destination: The destination dictionary.

    Returns:
        The merged dictionary.
    """
    for key, value in source.items():
        if isinstance(value, collections.abc.Mapping):
            destination[key] = deepmerge(value, destination.get(key, {}))
        else:
            destination[key] = value
    return destination
