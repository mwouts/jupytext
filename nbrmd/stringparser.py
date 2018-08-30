"""A simple file parser that can tell whether the first character of a line
is quoted or not"""


class StringParser:
    """A simple file parser that can tell whether the first character of a line
    is quoted or not"""
    single = None
    triple = None

    def __init__(self, language):
        self.ignore = language is None
        self.python = language != 'R'

    def is_quoted(self):
        """Is the next line quoted?"""
        if self.ignore:
            return False
        return self.single or self.triple

    def read_line(self, line):
        """Read a new line"""
        if self.ignore:
            return

        for i, char in enumerate(line):
            if char not in ['"', "'"]:
                continue
            # Is the char escaped?
            if line[i - 1:i] == '\\':
                continue

            if self.single == char:
                self.single = None
                continue
            if self.single is not None:
                continue

            if not self.python:
                continue

            if self.triple == char:
                if line[i - 2:i + 1] == 3 * char:
                    self.triple = None
                    continue
            if self.triple is not None:
                continue
            if line[i - 2:i + 1] == 3 * char:
                self.triple = char
                continue
            self.single = char

        # Line ended
        if self.python:
            self.single = None
