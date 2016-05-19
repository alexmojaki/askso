from textwrap import dedent


def multiline(message):
    return dedent(message).strip()


def write_to_path(path, text):
    with open(path, 'w') as f:
        f.write(text)


def read_from_path(path):
    with open(path) as f:
        return f.read()
