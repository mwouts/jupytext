# Testing a Jupyter notebook with pytest

In this notebook we describe how to test a notebook with `jupytext`.

## Writing assertions and tests in a notebook

Our notebook defines a function that we wish to test. Our function is simply

```python
def f(x, n=5):
    return [x + i for i in range(n)] 
```

We can test the assertion in Jupyter with simply

```python
assert f(5) == [5,6,7,8,9]
```

Since the assertion above works, we don't get any message. It's more interesting to see what happens when an assertion fails. Remove one element of the list above and change the assertion to, say, 

    assert f(5) == [5,6,8,9]

When we run the above in Jupyter, we get

```stderr
---------------------------------------------------------------------------
AssertionError                            Traceback (most recent call last)
<ipython-input-3-1383ac5d204f> in <module>
----> 1 assert f(5) == [5,6,8,9]

AssertionError: 
```

Now if we run the notebook with `jupytext --check pytest 'Tests in a notebook.md'`, we get a more detailed description of the issue, thanks to `pytest`'s rewriting of assertions: 
```output
[jupytext] Reading Tests in a notebook.md
=========================== test session starts ===========================
platform win32 -- Python 3.7.5, pytest-5.2.2, py-1.8.0, pluggy-0.13.0
rootdir: C:\Users\Marco
collected 0 items / 1 errors

================================ ERRORS ===================================
_________ ERROR collecting Tests in a notebook vhs_lscr.py ________________
Tests in a notebook vhs_lscr.py:19: in <module>
    assert f(5) == [5,6,8,9]
E   assert [5, 6, 7, 8, 9] == [5, 6, 8, 9]
E    +  where [5, 6, 7, 8, 9] = <function f at 0x000002440A0D1798>(5)
!!!!!!!!!!!!! Interrupted: 1 errors during collection !!!!!!!!!!!!!!!!!!!!!
=========================== 1 error in 0.09s ==============================
```

Once all of our assertions pass, we can move them to a test function. In Jupyter the function is not evaluated - only when we run `jupytext --check pytest` on the notebook, the function is actually executed.

```python
def test_f():
    assert f(5) == [5,6,7,8,9]
```

## Going further

- [nbval](https://github.com/computationalmodelling/nbval) is a plugin for `pytest` that allows you to make sure that Jupyter notebooks run properly, and that their new outputs match the current ones. Use it as `pytest --nbval notebook.ipynb`.
- [ipytest](https://github.com/chmp/ipytest) defines a `%%run_pytest` cell magic that allows you to execute the tests in a cell directly in Jupyter.
