from nbrmd.chunk_options import to_metadata, to_chunk_options, \
    parse_rmd_options, RMarkdownOptionParsingError
import pytest
import sys

samples = [('r', ('R', {})),
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
                        'echo': '{sum(a+c(1,2))>1}'}))
           ]


@pytest.mark.parametrize('options,language_and_metadata', samples)
def test_parse_options(options, language_and_metadata):
    assert to_metadata(options) == language_and_metadata


@pytest.mark.skipif(sys.version_info < (3, 6),
                    reason="unordered dict result in changes in chunk options")
@pytest.mark.parametrize('options,language_and_metadata', samples)
def test_build_options(options, language_and_metadata):
    assert to_chunk_options(*language_and_metadata) == options


@pytest.mark.parametrize('options,language_and_metadata', samples)
def test_build_options_random_order(options, language_and_metadata):
    # Older python has no respect for order...
    # assert to_chunk_options(metadata) == options

    def split_and_strip(opt):
        set([o.strip() for o in opt.split(',')])

    assert (split_and_strip(to_chunk_options(*language_and_metadata)) ==
            split_and_strip(options))


@pytest.mark.parametrize('options', ['a={)', 'name, name2',
                                     'a=}', 'b=]', 'c=['])
def test_parsing_error(options):
    with pytest.raises(RMarkdownOptionParsingError):
        parse_rmd_options(options)
