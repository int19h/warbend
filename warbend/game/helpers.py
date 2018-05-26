from __future__ import absolute_import, division, print_function

__all__ = ['varnames', 'slot_enum', 'slot_array', 'groups_from']

import sys

from .. import data
from ..data import array, enum, int64
from ..util.frozendict import frozendict
from ..util.memoize import memoize
from .module_system import module_constants


@memoize
def varnames(module, *prefixes, **kwargs):
    frozen = kwargs.pop('frozen', True)
    exclude_prefixes = kwargs.pop('exclude_prefixes', ())
    assert not kwargs

    def excluded(name):
        for prefix in exclude_prefixes:
            if name.startswith(prefix):
                return True
        return False

    names = []
    for prefix in prefixes:
        names += [name for name in vars(module)
                  if name.startswith(prefix) and not excluded(name)]

    res = {getattr(module, name): name for name in names}
    if frozen:
        res = frozendict(res)
    return res


@memoize
def slot_enum(*prefixes):
    return enum(int64, varnames(module_constants, *prefixes))


def slot_array(*prefixes, **kwargs):
    extra_keys = kwargs.pop('extra_keys', {})
    exclude_prefixes = kwargs.pop('exclude_prefixes', ())
    keys = varnames(module_constants, *prefixes, frozen=False,
                    exclude_prefixes=exclude_prefixes)
    keys.update(extra_keys)
    keys = frozendict(keys)

    def f(record):
        return array(int64, record.num_slots, singular='slot', keys=keys, **kwargs)
    return staticmethod(f)


@memoize
def groups_from(id_module):
    marker_module = module_constants

    class Groups(object):
        def __getitem__(self, name):
            try:
                begin_name = getattr(marker_module, name + '_begin')
                end_name = getattr(marker_module, name + '_end')
                begin = getattr(id_module, begin_name)
                end = getattr(id_module, end_name)
            except AttributeError:
                raise KeyError()
            return begin, end

    return Groups()
