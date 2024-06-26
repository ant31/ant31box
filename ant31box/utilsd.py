#!/usr/bin/env python3
from typing import Mapping


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
