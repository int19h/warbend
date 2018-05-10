from __future__ import absolute_import, division, print_function

from .. import mode
from ..util.io import eprintf
from .errors import ValidationError

warn_on_coerce = mode.is_interactive


def no_coerce_warnings():
    class NoCoerceWarningsContextManager(object):
        def __enter__(self):
            global warn_on_coerce
            self.saved = warn_on_coerce
            warn_on_coerce = False

        def __exit__(self, *args):
            global warn_on_coerce
            warn_on_coerce = self.saved

    return NoCoerceWarningsContextManager()


def validate(value):
    try:
        validate = value._validate
    except AttributeError:
        pass
    else:
        validate()


def coerce(parent, selector, value, t):
    from .array import Array, is_array
    from .record import Record
    if type(value) is t:
        if getattr(value, '_dirty', True):
            validate(value)
        return value
    initial_value = value
    errmsg = None
    if not issubclass(t, Record):
        if warn_on_coerce:
            eprintf("Coercing '{}' to '{}'\n",
                    type(value).__name__, t.__name__)
        if issubclass(t, Array):
            if is_array(value):
                try:
                    value = t(value, parent=parent, selector=selector)
                except (TypeError, ValueError):
                    value = None
                else:
                    value._validate()
                    return value
        else:
            try:
                value = t(value)
                validate(value)
            except (TypeError, ValueError) as ex:
                value = None
                errmsg = str(ex)
        if type(value) is t:
            return value
    if not errmsg:
        errmsg = "couldn't coerce value of type '{}' to expected type '{}'".format(
            type(initial_value).__name__, t.__name__)
    from .mutable import path
    raise ValidationError(path(parent, selector), errmsg)
