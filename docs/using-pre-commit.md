# Using as a pre-commit hook

Jupytext works well with the [pre-commit](https://pre-commit.com/) framework. You can add the following to your `.pre-commit-config.yaml` file to sync all staged notebooks:

```yaml
repos:
-   repo: https://github.com/mwouts/jupytext
    rev: #CURRENT_TAG/COMMIT_HASH
    hooks:
    - id: jupytext
      args: [--sync]
```

You can provide almost all command line arguments to Jupytext in pre-commit, for example to produce several kinds of output files:

```yaml
repos:
-   repo: https://github.com/mwouts/jupytext
    rev: #CURRENT_TAG/COMMIT_HASH
    hooks:
    - id: jupytext
      args: [--from, ipynb, --to, "py:percent"]
```

If you are combining Jupytext with other pre-commit hooks, you must ensure that all hooks will pass on any files you generate. For example, if you have a hook for using `black` to format all your python code, then you should use Jupytext's `--pipe` option to also format newly generated Python scripts before writing them:

```yaml
repos:
-   repo: https://github.com/mwouts/jupytext
    rev: #CURRENT_TAG/COMMIT_HASH
    hooks:
    - id: jupytext
      args: [--sync, --pipe, black]
      additional_dependencies:
        - black==19.10b0 # Matches hook

-   repo: https://github.com/psf/black
    rev: 19.10b0
    hooks:
    - id: black
      language_version: python3
```
