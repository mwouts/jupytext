# Contributing

Thanks for reading this. Contributions to this project are welcome.
And there are many ways you can contribute...

## Spread the word

You like Jupytext? Probably your friends and colleagues will like it too.
Show them what you've been able to do with: version control, collaboration on notebooks, refactoring of notebooks, notebooks integrated in library, notebook generated from Markdown documents...

By the way, we're also interested to know how you use Jupytext! There may well be applications we've not thought of!

## Improve the documentation

You think the documentation could be improved? You've spotted a typo, or you think you can rephrase a paragraph to make is easier to follow? Please follow the _Edit on Github_ link, edit the document, and submit a pull request.

## Report an issue

You have seen an issue with Jupytext, or you can't find your way in the documentation?
Please let us know, and provide enough information so that we can reproduce the problem.

## Propose enhancements

You want to submit an enhancement on Jupytext? Unless this is a small change, we usually prefer that you let us know beforehand: open an issue that describe the problem you want to solve.

## Add support for another language

A pull request for which you do not need to contact us in advance is the addition of a new language to Jupytext. In principle that should be easy - you would only have to:
- document the language extension and comment by adding one line to `_SCRIPT_EXTENSIONS` in `languages.py`.
- add the language to `docs/languages.md`
- contribute a sample notebook in `tests/notebooks/ipynb_[language]`.
- run the tests suite (with just `pytest`). The mirror tests will generate various text representations corresponding to your notebook under  `tests/notebooks/mirror/`. Please verify that these files are valid scripts, and commit them.
