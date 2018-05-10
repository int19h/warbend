from __future__ import absolute_import, division, print_function

from ..serialization import binary
from ..util.io import maybe_open, source, eprintf


def load(module, reader, format=binary, options=None):
    reader = maybe_open(reader, 'rb')
    eprintf('Reading {} save: {}\n', format.format_name, source(reader))
    return format.load(module.game, reader, options)


def save(game, writer, format=binary, options=None):
    writer = maybe_open(writer, 'wb')
    eprintf('Writing {} save: {}\n', format.format_name, source(writer))
    return format.save(game, writer, options)
