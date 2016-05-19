from __future__ import print_function

from askso.utils import multiline


class QuietExit(Exception):
    pass


class AccessRecorder(object):
    def __init__(self):
        self.accessed = False

    def __getattr__(self, _):
        self.accessed = True
        raise QuietExit


class FileTracker(object):
    def __init__(self, open_function):
        self.open_function = open_function
        self.paths = []
        self.non_ascii_files = []

    def __call__(self, *args, **kwargs):
        if args and isinstance(args[0], str) and args[0] not in self.paths:
            self.paths.append(args[0])
        return self.open_function(*args, **kwargs)

    def result(self):
        result = []
        for path in self.paths:
            data = self.try_read(path)
            if data is not None:
                result.append({'path': path, 'data': data})
                if len(result) > 3:
                    break
        return result

    def try_read(self, path):
        try:
            with open(path) as f:
                max_lines = 15
                max_bytes = max_lines * 200
                data = f.read(max_bytes + 1).decode('ascii')

            if len(data) > max_bytes or len(data.splitlines()) > max_lines:
                return multiline("""
                    This file is too long.
                    All files opened must be within %s bytes and %s lines at the end of the program.
                    This is so that their contents can easily be included in the question.
                    Cut down your data and code to the minimum you need to show the problem.
                    """ % (max_bytes, max_lines))

            return data

        except IOError:
            pass
        except UnicodeDecodeError:
            self.non_ascii_files.append(path)
