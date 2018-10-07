import pytest
from jupytext.formats import guess_format
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


def test_script_with_spyder_cell_with_name_is_percent(script="""#%% cell name
1 + 2"""):
    assert guess_format(script, '.py') == 'percent'
