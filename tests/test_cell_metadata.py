import pytest
from jupytext.cell_metadata import rmd_options_to_metadata, \
    metadata_to_rmd_options, parse_rmd_options, RMarkdownOptionParsingError, \
    try_eval_metadata, json_options_to_metadata, md_options_to_metadata
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
             {'name': 'chunk_name', 'active': 'Rmd', 'hide_output': True}))
           ]


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
    assert metadata_to_rmd_options('R', metadata) == 'r echo=FALSE'


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
    assert md_options_to_metadata('not_a_language') == (None, {
        'name': 'not_a_language'})
