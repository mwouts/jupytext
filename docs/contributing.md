# Contributing

Thanks for reading this! Contributions to this project are welcome, and there are many ways you can contribute

## Improve the documentation

You've spotted a typo, a paragraph that is not very clear, or an instruction that does not work? Please follow the _Fork me on Github_ link, edit the document, and submit a pull request.

## Report an issue

You have seen an issue with Jupytext, or you can't find your way in the documentation?
Please let us know, and provide enough information so that we can reproduce the problem.

## Propose enhancements

You want to submit an enhancement on Jupytext? Unless this is a small change, we usually prefer that you let us know beforehand: open an issue that describe the problem you want to solve.

## Add support for another language

A pull request for which you do not need to contact us in advance is the addition of a new language to Jupytext. In principle that should be easy - you would only have to:
- document the language extension and comment by adding one line to `_SCRIPT_EXTENSIONS` in `jupytext/languages.py`.
- add the language to `docs/languages.md`
- contribute a sample notebook in `tests/data/notebooks/inputs/ipynb_[language]`.
- run the tests suite (create a [development environment](developing.md), then execute `pytest` locally). The tests will generate various text representations corresponding to your notebook under  `tests/data/notebooks/outputs/`. Please verify that these files are valid scripts, and include them in your PR.
