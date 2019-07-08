import pytest
from jupytext.compare import compare
from jupytext.cell_metadata import rmd_options_to_metadata, metadata_to_rmd_options, parse_rmd_options
from jupytext.cell_metadata import _IGNORE_CELL_METADATA, RMarkdownOptionParsingError, try_eval_metadata
from jupytext.cell_metadata import json_options_to_metadata, metadata_to_json_options
from jupytext.cell_metadata import md_options_to_metadata, metadata_to_md_options
from jupytext.metadata_filter import filter_metadata
from .utils import skip_if_dict_is_not_ordered

SAMPLES = [('r', ('R', {})),
           ('r plot_1, dpi=72, fig.path="fig_path/"',
            ('R', {'name': 'plot_1', 'dpi': 72, 'fig.path': '"fig_path/"'})),
           ("r plot_1, bool=TRUE, fig.path='fig_path/'",
            ('R', {'name': 'plot_1', 'bool': True,
                   'fig.path': "'fig_path/'"})),
           ('r echo=FALSE',
            ('R', {'hide_input': True})),
           ('r plot_1, echo=TRUE',
            ('R', {'name': 'plot_1', 'hide_input': False})),
           ('python echo=if a==5 then TRUE else FALSE',
            ('python', {'echo': 'if a==5 then TRUE else FALSE'})),
           ('python noname, tags=c("a", "b", "c"), echo={sum(a+c(1,2))>1}',
            ('python', {'name': 'noname', 'tags': ['a', 'b', 'c'],
                        'echo': '{sum(a+c(1,2))>1}'})),
           ('python active="ipynb,py"',
            ('python', {'active': 'ipynb,py'})),
           ('python include=FALSE, active="Rmd"',
            ('python', {'active': 'Rmd', 'hide_output': True})),
           ('r chunk_name, include=FALSE, active="Rmd"',
            ('R',
             {'name': 'chunk_name', 'active': 'Rmd', 'hide_output': True})),
           ('python tags=c("parameters")',
            ('python', {'tags': ['parameters']}))]


@pytest.mark.parametrize('options,language_and_metadata', SAMPLES)
def test_parse_rmd_options(options, language_and_metadata):
    assert rmd_options_to_metadata(options) == language_and_metadata


@skip_if_dict_is_not_ordered
@pytest.mark.parametrize('options,language_and_metadata', SAMPLES)
def test_build_options(options, language_and_metadata):
    assert metadata_to_rmd_options(*language_and_metadata) == options


@pytest.mark.parametrize('options,language_and_metadata', SAMPLES)
def test_build_options_random_order(options, language_and_metadata):
    # Older python has no respect for order...
    # assert to_chunk_options(metadata) == options

    def split_and_strip(opt):
        set([o.strip() for o in opt.split(',')])

    assert (split_and_strip(metadata_to_rmd_options(*language_and_metadata)) ==
            split_and_strip(options))


@pytest.mark.parametrize('options', ['a={)', 'name, name2',
                                     'a=}', 'b=]', 'c=['])
def test_parsing_error(options):
    with pytest.raises(RMarkdownOptionParsingError):
        parse_rmd_options(options)


def test_ignore_metadata():
    metadata = {'trusted': True, 'hide_input': True}
    metadata = filter_metadata(metadata, None, _IGNORE_CELL_METADATA)
    assert metadata_to_rmd_options('R', metadata) == 'r echo=FALSE'


def test_filter_metadata():
    assert filter_metadata({'scrolled': True}, None, _IGNORE_CELL_METADATA) == {}


def test_try_eval_metadata():
    metadata = {'list': 'list("a",5)',
                'c': 'c(1,2,3)'}
    try_eval_metadata(metadata, 'list')
    try_eval_metadata(metadata, 'c')
    assert metadata == {'list': ['a', 5], 'c': [1, 2, 3]}


def test_parse_wrong_json():
    assert json_options_to_metadata("""{"key":'incorrect value'}""") == {}


def test_parse_md_options():
    assert md_options_to_metadata('python') == ('python', {})
    assert md_options_to_metadata('not_a_language') == (None, {'not_a_language': None})


def test_round_trip_md_options(metadata={'.class': None,
                                         'long-and-str$ange.name': None,
                                         'string': "Hello",
                                         'number': .21,
                                         'array': ['First', 'Second', 3, "string with single ' in it'"],
                                         'dict': {"a": 5, "b": [1.2, "four"]},
                                         '.another_class': None}):
    options = metadata_to_md_options(metadata)
    language, metadata2 = md_options_to_metadata('python ' + options)
    assert language == 'python'
    compare(metadata, metadata2)


def test_write_parse_json():
    metadata = {"tags": ["parameters"]}
    options = metadata_to_json_options(metadata)
    metadata2 = json_options_to_metadata(options, add_brackets=False)
    assert metadata == metadata2
