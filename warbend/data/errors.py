from __future__ import absolute_import, division, print_function


class ValidationError(Exception):
    def __init__(self, path, message, *args, **kwargs):
        msg = '%r: %s' % (path, message)
        super(ValidationError, self).__init__(msg, *args, **kwargs)
        self.path = path
