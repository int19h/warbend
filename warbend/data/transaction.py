from __future__ import absolute_import, division, print_function

from .. import mode
from ..util.io import eprintf
from ..util.progress import ProgressBar
from .coerce import no_coerce_warnings


class Transaction(object):
    __slots__ = ['context', 'active', 'is_automatic']

    def __init__(self, context):
        self.context = context
        self.active = 0

    def __nonzero__(self):
        return self.active > 0

    def __enter__(self):
        self.begin()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.commit(True)
        else:
            self.rollback(True)

    def __repr__(self):
        if not self.active:
            return '<no active transaction>'
        elif self.is_automatic:
            return '<automatic transaction>'
        else:
            return '<explicit transaction>'

    def begin(self, automatic=False):
        if not self.active:
            self.is_automatic = automatic
        self.active += 1
        return self

    def rollback(self, if_active=False):
        if not self.active:
            if if_active:
                return
            else:
                raise RuntimeError('No active transaction')
        for obj in self.context.mutable.itervalues():
            obj._revert_changes()
        self.active = 0
        if mode.is_interactive and not self.is_automatic:
            eprintf('Changes reverted.\n')

    def commit(self, if_active=False):
        if not self.active:
            if if_active:
                return
            else:
                raise RuntimeError('No active transaction')
        if self.active > 1:
            self.active -= 1
            return
        context = self.context
        need_validation = {}
        for obj in context.mutable.itervalues():
            if obj._dirty:
                need_validation.update(obj._observers)
        if need_validation:
            log_validation = mode.is_interactive or len(need_validation) > 1
            with no_coerce_warnings():
                if log_validation:
                    eprintf('Validating {:n} affected objects', len(need_validation))
                if len(need_validation) > 1000:
                    if log_validation:
                        eprintf(':\n')
                    with ProgressBar('validate', len(need_validation)) as progress:
                        for obj in need_validation.itervalues():
                            try:
                                obj._validate()
                            except:
                                if log_validation:
                                    eprintf('error!\n')
                                raise
                            progress.report(1)
                else:
                    if log_validation:
                        eprintf(' ... ')
                    for obj in need_validation.itervalues():
                        try:
                            obj._validate()
                        except:
                            if log_validation:
                                eprintf('error!\n')
                            raise
                    if log_validation:
                        eprintf('done!\n')
        for obj in context.mutable.itervalues():
            obj._commit_changes()
        self.active = 0
        return need_validation.itervalues()
