from __future__ import print_function

import os
import platform
import sys
import traceback as tb
try:
    # noinspection PyCompatibility
    from StringIO import StringIO
except ImportError:
    from io import StringIO
from contextlib import contextmanager
from tempfile import gettempdir

from askso.utils import write_to_path
from files import AccessRecorder, QuietExit, FileTracker


@contextmanager
def temp_vars(*var_list):
    holders = []
    try:
        for var in var_list:
            h = Holder()
            h.module, h.name, h.value = var
            h.old = getattr(h.module, h.name)
            setattr(h.module, h.name, h.value)
            holders.append(h)
        yield
    finally:
        for h in holders:
            setattr(h.module, h.name, h.old)


class Holder(object):
    pass


def execute(code):
    if code == 'test_error':
        raise ValueError
    tempdir = gettempdir()
    script_py = os.path.join(tempdir, 'my_script.py')
    write_to_path(script_py, code)
    stdin = AccessRecorder()
    stdout = StringIO()
    stderr = StringIO()
    file_tracker = FileTracker(open)
    with temp_vars([sys, 'stdout', stdout],
                   [sys, 'stderr', stderr],
                   [sys, 'stdin', stdin]):

        # noinspection PyBroadException
        try:
            exec (
                compile(code, script_py, 'exec', dont_inherit=True),
                {'open': file_tracker, '__name__': '__main__'},
                {})
        except QuietExit:
            pass
        except:
            tb_list = [e for e in tb.extract_tb(sys.exc_info()[2]) if os.path.dirname(__file__) not in e[0]]
            print('Traceback (most recent call last):\n' +
                  ''.join(tb.format_list(tb_list) +
                          tb.format_exception_only(*sys.exc_info()[:2])).replace(tempdir, ''),
                  file=sys.stderr)
    return {'stdout': stdout.getvalue(),
            'stderr': stderr.getvalue(),
            'files': file_tracker.result(),
            'stdin_used': stdin.accessed,
            'non_ascii_files': file_tracker.non_ascii_files,
            'version': platform.python_version()}
