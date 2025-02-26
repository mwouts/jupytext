"""Determine how many blank lines should be inserted between two cells"""
from .stringparser import StringParser


def next_instruction_is_function_or_class(lines):
    """Is the first non-empty, non-commented line of the cell either a function or a class?"""
    parser = StringParser("python")
    for i, line in enumerate(lines):
        if parser.is_quoted():
            parser.read_line(line)
            continue
        parser.read_line(line)
        if not line.strip():  # empty line
            if i > 0 and not lines[i - 1].strip():
                return False
            continue
        if (
            line.startswith("def ")
            or line.startswith("async ")
            or line.startswith("class ")
        ):
            return True
        if line.startswith(("#", "@", " ", ")")):
            continue
        return False

    return False


def cell_ends_with_function_or_class(lines):
    """Does the last line of the cell belong to an indented code?"""
    non_quoted_lines = []
    parser = StringParser("python")
    for line in lines:
        if not parser.is_quoted():
            non_quoted_lines.append(line)
        parser.read_line(line)

    # find the first line, starting from the bottom, that is not indented
    lines = non_quoted_lines[::-1]
    for i, line in enumerate(lines):
        if not line.strip():
            # two blank lines? we won't need to insert more blank lines below this cell
            if i > 0 and not lines[i - 1].strip():
                return False
            continue
        if line.startswith(("#", " ", ")")):
            continue
        if (
            line.startswith("def ")
            or line.startswith("async ")
            or line.startswith("class ")
        ):
            return True
        return False

    return False


def cell_ends_with_code(lines):
    """Is the last line of the cell a line with code?"""
    if not lines:
        return False
    if not lines[-1].strip():
        return False
    if lines[-1].startswith("#"):
        return False
    return True


def cell_has_code(lines):
    """Is there any code in this cell?"""
    for i, line in enumerate(lines):
        stripped_line = line.strip()
        if stripped_line.startswith("#"):
            continue

        # Two consecutive blank lines?
        if not stripped_line:
            if i > 0 and not lines[i - 1].strip():
                return False
            continue

        return True

    return False


def pep8_lines_between_cells(prev_lines, next_lines, ext):
    """How many blank lines should be added between the two python paragraphs to make them pep8?"""
    if not next_lines:
        return 1
    if not prev_lines:
        return 0
    if ext != ".py":
        return 1
    if cell_ends_with_function_or_class(prev_lines):
        return 2 if cell_has_code(next_lines) else 1
    if cell_ends_with_code(prev_lines) and next_instruction_is_function_or_class(
        next_lines
    ):
        return 2
    return 1
