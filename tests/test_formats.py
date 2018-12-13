import pytest
from jupytext.formats import guess_format, read_format_from_metadata
from .utils import list_notebooks


@pytest.mark.parametrize('nb_file', list_notebooks('python'))
def test_guess_format_light(nb_file):
    with open(nb_file) as stream:
        assert guess_format(stream.read(), ext='.py') == 'light'


@pytest.mark.parametrize('nb_file', list_notebooks('percent'))
def test_guess_format_percent(nb_file):
    with open(nb_file) as stream:
        assert guess_format(stream.read(), ext='.py') == 'percent'


@pytest.mark.parametrize('nb_file', list_notebooks('sphinx'))
def test_guess_format_sphinx(nb_file):
    with open(nb_file) as stream:
        assert guess_format(stream.read(), ext='.py') == 'sphinx'


def test_script_with_magics_not_percent(script="""# %%time
1 + 2"""):
    assert guess_format(script, '.py') == 'light'


def test_script_with_spyder_cell_is_percent(script="""#%%
1 + 2"""):
    assert guess_format(script, '.py') == 'percent'


def test_script_with_percent_cell_and_magic_is_hydrogen(script="""#%%
%matplotlib inline
"""):
    assert guess_format(script, '.py') == 'hydrogen'


def test_script_with_spyder_cell_with_name_is_percent(script="""#%% cell name
1 + 2"""):
    assert guess_format(script, '.py') == 'percent'


def test_read_format_from_metadata(script="""---
jupyter:
  jupytext:
    formats: ipynb,pct.py:percent,lgt.py:light,spx.py:sphinx,md,Rmd
    text_representation:
      extension: .pct.py
      format_name: percent
      format_version: '1.1'
      jupytext_version: 0.8.0
---"""):
    assert read_format_from_metadata(script, '.Rmd') is None
