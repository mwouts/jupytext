# Advanced functionality

Below are some advanced functionality and tips.

## Fine tuning

Jupyter magic commands are commented when exporting the notebook to text, except for the `markdown` and the `hydrogen` format. If you want to change this for a single line, add a `#escape` or `#noescape` flag on the same line as the magic, or a `"comment_magics": true` or `false` entry in the notebook metadata, in the `"jupytext"` section. Or set your preference globally on the contents manager by adding this line to `.jupyter/jupyter_notebook_config.py`:
```python
c.ContentsManager.comment_magics = True # or False
```

Also, you may want some cells to be active only in the Python, or R Markdown representation. For this, use the `active` cell metadata. Set `"active": "ipynb"` if you want that cell to be active only in the Jupyter notebook. And `"active": "py"` if you want it to be active only in the Python script. And `"active": "ipynb,py"` if you want it to be active in both, but not in the R Markdown representation...

## Extending the `light` and `percent` formats to more languages

You want to extend the `light` and `percent` format to another language? In principle that is easy, and you will only have to:
- document the language extension and comment by adding one line to `_SCRIPT_EXTENSIONS` in `languages.py`.
- contribute a sample notebook in `tests\notebooks\ipynb_[language]`.
- add two tests in `test_mirror.py`: one for the `light` format, and another one for the `percent` format.
- Make sure that the tests pass, and that the text representations of your notebook, found in  `tests\notebooks\mirror\ipynb_to_script` and `tests\notebooks\mirror\ipynb_to_percent`, are valid scripts.