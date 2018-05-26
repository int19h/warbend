from __future__ import absolute_import, division, print_function

from numbers import Integral
import operator
from os.path import commonprefix

from .array import Array, is_array


class IdRef(object):
    __slots__ = ['target']
    __slots__ = []

    base_type = type(None)
    target_func = staticmethod(lambda root: Array())

    def _validate(self, context):
        try:
            validate = self.base_type._validate
        except AttributeError:
            pass
        else:
            validate(self, context)

        self.target = target = self.target_func(context.root)
        if self != -1 and not (0 <= self < len(target)):
            raise ValueError('{} is outside of valid range ({}:{}) for {}'.format(
                self, 0, len(target), type(self).__name__))
    
    def __repr__(self):
        target = self.target
        sel = self.base_type(self)
        if target is None:
            path = '<?>'
        else:
            assert is_array(target), target
            path = target._path
            if sel == -1:
                sel = None
            else:
                sel = type(target).keys.get(sel, sel)
        return '{}[{!r}]'.format(path, sel)


def id_ref(t, target_func):
    assert issubclass(t, Integral), t
    assert callable(target_func), target_func

    class IdRefT(IdRef, t):
        __slots__ = ['target']

    IdRefT.__name__ = 'idref(%s)' % t.__name__
    IdRefT.base_type = t
    IdRefT.target_func = staticmethod(target_func)
    return IdRefT
