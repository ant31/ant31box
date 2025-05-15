#!/usr/bin/env python3
import importlib
from collections.abc import Mapping
from typing import Any


# from uvicorn.importer (BSD 3-Clause https://github.com/encode/uvicorn/blob/master/LICENSE.md)
class ImportFromStringError(Exception):
    pass


# From uvicorn.importer (BSD 3-Clause https://github.com/encode/uvicorn/blob/master/LICENSE.md)
def import_from_string(import_str: Any) -> Any:
    if not isinstance(import_str, str):
        return import_str

    module_str, _, attrs_str = import_str.partition(":")
    if not module_str or not attrs_str:
        message = 'Import string "{import_str}" must be in format "<module>:<attribute>".'
        raise ImportFromStringError(message.format(import_str=import_str))

    try:
        module = importlib.import_module(module_str)
    except ModuleNotFoundError as exc:
        if exc.name != module_str:
            raise exc from None
        message = 'Could not import module "{module_str}".'
        raise ImportFromStringError(message.format(module_str=module_str))

    instance = module
    try:
        for attr_str in attrs_str.split("."):
            instance = getattr(instance, attr_str)
    except AttributeError:
        message = 'Attribute "{attrs_str}" not found in module "{module_str}".'
        raise ImportFromStringError(message.format(attrs_str=attrs_str, module_str=module_str))

    return instance


def deepmerge(dct, merge_dct):
    """Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
    updating only top-level keys, dict_merge recurses down into dicts nested
    to an arbitrary depth, updating keys. The ``merge_dct`` is merged into
    ``dct``.
    :param dct: dict onto which the merge is executed
    :param merge_dct: dct merged into dct
    :return: None
    """
    for k, _ in merge_dct.items():
        if k in dct and isinstance(dct[k], Mapping) and isinstance(merge_dct[k], Mapping):
            deepmerge(dct[k], merge_dct[k])
        else:
            dct[k] = merge_dct[k]
