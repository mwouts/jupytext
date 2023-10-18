"""Raise the given error at evaluation time"""


def reraise(error):
    """Return a function that raises the given error when evaluated"""

    def local_function(*args, **kwargs):
        raise error

    return local_function
