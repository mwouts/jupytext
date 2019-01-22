import pytest
from testfixtures import compare
from jupytext import readf, reads, writes
from jupytext.pep8 import next_instruction_is_function_or_class, cell_ends_with_function_or_class
from .utils import list_notebooks


def test_next_instruction_is_function_or_class():
    text = """@pytest.mark.parametrize('py_file', 
    [py_file for py_file in list_notebooks('../jupytext') + list_notebooks('.') if
                                     py_file.endswith('.py')])
def test_no_metadata_when_py_is_pep8(py_file):
    pass
"""
    assert next_instruction_is_function_or_class(text.splitlines())


def test_cell_ends_with_function_or_class():
    text = """class A:
    __init__():
    '''A docstring
with two lines or more'''
        self.a = 0
"""
    assert cell_ends_with_function_or_class(text.splitlines())


def test_pep8():
    text = """import os

path = os.path


# code cell #1, with a comment on f
def f(x):
    return x + 1


# markdown cell #1

# code cell #2 - an instruction
a = 4


# markdown cell #2

# code cell #3 with a comment on g
def g(x):
    return x + 1


# markdown cell #3

# the two lines are:
# - right below the function/class
# - below the last python paragraph (i.e. NOT ABOVE g)

# code cell #4
x = 4
"""
    nb = reads(text, 'py')
    for cell in nb.cells:
        assert not cell.metadata

    text2 = writes(nb, 'py')
    compare(text, text2)


@pytest.mark.parametrize('py_file', [py_file for py_file in list_notebooks('../jupytext') + list_notebooks('.') if
                                     py_file.endswith('.py')])
def test_no_metadata_when_py_is_pep8(py_file):
    nb = readf(py_file)

    for i, cell in enumerate(nb.cells):
        if i == 0 and not cell.source:
            assert cell.metadata == {'lines_to_next_cell': 0}, py_file
        else:
            assert not cell.metadata, (py_file, cell.source)
