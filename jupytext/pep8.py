"""Determine how many blank lines should be inserted between two cells"""


def next_instruction_is_function_or_class(lines):
    """Is the first non-empty, non-commented line of the cell either a function or a class?"""
    prev_line_blank = False
    for line in lines:
        if not line.strip():  # empty line
            if prev_line_blank:
                return False
            prev_line_blank = True
            continue
        if line.startswith('def ') or line.startswith('class '):
            return True
        if line.startswith(('#', '@', ' ')):
            prev_line_blank = False
            continue
        return False

    return False


def cell_ends_with_function_or_class(lines):
    """Does the last line of the cell belong to an indented code?"""
    if not lines:
        return False
    if not lines[-1].startswith(' '):
        return False
    if not lines[-1].strip():
        return False

    # find the first line, starting from the bottom, that is not indented
    prev_line_blank = False
    for line in lines[::-1]:
        if not line.strip():
            if prev_line_blank:
                return False
            prev_line_blank = True
            continue
        prev_line_blank = False
        if line.startswith('#') or line.startswith(' '):
            continue
        if line.startswith('def ') or line.startswith('class '):
            return True
        return False

    return False


def cell_ends_with_code(lines):
    """Is the last line of the cell a line with code?"""
    if not lines:
        return False
    if not lines[-1].strip():
        return False
    if lines[-1].startswith('#'):
        return False
    return True


def pep8_lines_between_cells(prev_lines, next_lines, ext):
    """How many blank lines should be added between the two python paragraphs to make them pep8?"""
    if not next_lines:
        return 1
    if not prev_lines:
        return 0
    if ext != '.py':
        return 1
    if cell_ends_with_function_or_class(prev_lines):
        return 2
    if cell_ends_with_code(prev_lines) and next_instruction_is_function_or_class(next_lines):
        return 2
    return 1
