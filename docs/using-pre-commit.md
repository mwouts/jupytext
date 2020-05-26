# Pre-commit hooks

## Jupytext as a Git pre-commit hook

Jupytext is also available as a Git pre-commit hook. Use this if you want Jupytext to create and update the `.py` (or `.md`...) representation of the staged `.ipynb` notebooks. All you need is to create an executable `.git/hooks/pre-commit` file with the following content:
```bash
#!/bin/sh
# For every ipynb file in the git index, add a Python representation
jupytext --from ipynb --to py:light --pre-commit
```

```bash
#!/bin/sh
# For every ipynb file in the git index:
# - apply black and flake8
# - export the notebook to a Python script in folder 'python'
# - and add it to the git index
jupytext --from ipynb --pipe black --check flake8 --pre-commit
jupytext --from ipynb --to python//py:light --pre-commit
```

If you don't want notebooks to be committed (and only commit the text representations), you can ask the pre-commit hook to unstage notebooks after conversion by adding the following line:
```bash
git reset HEAD **/*.ipynb
```
Note that these hooks do not update the `.ipynb` notebook when you pull. Make sure to either run `jupytext` in the other direction, or to use our paired notebook and our contents manager for Jupyter. Also, Jupytext does not offer a merge driver. If a conflict occurs, solve it on the text representation and then update or recreate the `.ipynb` notebook. Or give a try to nbdime and its [merge driver](https://nbdime.readthedocs.io/en/stable/vcs.html#merge-driver).

## Using Jupytext with the pre-commit package manager

Using Jupytext with the [pre-commit package manager](https://pre-commit.com/) is another option. You could add the following to your `.pre-commit-config.yaml` file:
```
repos:
-   repo: local
    hooks:
    - id: jupytext
      name: jupytext
      entry: jupytext --to md
      files: .ipynb
      language: python
```

Here is another `.pre-commit-config.yaml` example that uses the --pre-commit mode of Jupytext to convert all `.ipynb` notebooks to `py:light` representation and unstage the `.ipynb` files before committing.
```
repos:
  -
    repo: local
    hooks:
      -
        id: jupytext
        name: jupytext
        entry: jupytext --from ipynb --to py:light --pre-commit
        pass_filenames: false
        language: python
      -
        id: unstage-ipynb
        name: unstage-ipynb
        entry: git reset HEAD **/*.ipynb
        pass_filenames: false
        language: system

```
