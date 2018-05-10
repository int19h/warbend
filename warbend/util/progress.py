from __future__ import absolute_import, division, print_function

from datetime import timedelta
from sys import stderr
from time import time, clock

from .io import eprintf
from .. import mode


class ProgressBar(object):
    BAR_WIDTH = 50

    def __init__(self, name, total):
        self.name = name
        self.total = total

    def __enter__(self):
        self.start = time()
        self.current = 0
        self.callback(self.name, True)
        self.report(0, force_update=True)
        return self

    def __exit__(self, exc_type, *args):
        if not exc_type:
            self.current = self.total
        self.report(0, force_update=True)
        self.callback(self.name, False)
        eprintf('\n')

    def report(self, increase, force_update=False):
        total = self.total
        old_cur = self.current
        new_cur = old_cur + increase
        old_perc = int(old_cur / total * 100)
        new_perc = min(100, int(new_cur / total * 100))
        self.current = new_cur
        if force_update or old_perc != new_perc:
            self.print_progress(new_perc)

    def print_progress(self, percent):
        self.callback(self.name, percent)
        if mode.is_quiet or not stderr.isatty:
            return
        td = timedelta(seconds=int(time() - self.start))
        bar = '#' * (percent * self.BAR_WIDTH // 100)
        bar = bar.ljust(self.BAR_WIDTH, '-')
        eprintf('\r{:03d}% [{}] {}', percent, bar, td)

    @staticmethod
    def callback(name, percent):
        pass


class ProgressIO(object):
    __slots__ = ['f', 'report', 'current', 'progress']

    def __init__(self, name, f):
        self.f = f
        self.current = 0
        f.seek(0, 2)
        self.progress = ProgressBar(name, f.tell())
        f.seek(0)

    def __enter__(self):
        self.f.__enter__()
        self.progress.__enter__()
        return self

    def __exit__(self, *args):
        self.progress.__exit__(*args)
        self.f.__exit__(*args)

    def __getattr__(self, name):
        return getattr(self.f, name)

    def read(self, *args, **kwargs):
        data = self.f.read(*args, **kwargs)
        self.progress.report(len(data))
        return data

    def readinto(self, *args, **kwargs):
        n = self.f.readinto(*args, **kwargs)
        self.progress.report(n)
        return n

    def seekable(self):
        return False

    def writable(self):
        return False