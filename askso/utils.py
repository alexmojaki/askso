import sys
from codecs import open
from textwrap import dedent


def multiline(message):
    return dedent(message).strip()


def write_to_path(path, text):
    with open(path, 'w', encoding=sys.getfilesystemencoding()) as f:
        f.write(text)


def read_from_path(path):
    with open(path, encoding=sys.getfilesystemencoding()) as f:
        return f.read()
