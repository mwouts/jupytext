from nbrmd.chunk_options import to_metadata, to_chunk_options
import pytest
import sys

samples = [('r', {'language': 'R'}),
           ('r plot_1, dpi=72, fig.path="fig_path/"', {
               'language': 'R', 'name': 'plot_1', 'chunk_options': {'dpi': '72', 'fig.path': '"fig_path/"'}}),
           ('r echo=FALSE', {
               'language': 'R', 'hide_input': True}),
           ('r plot_1, echo=TRUE', {
               'language': 'R', 'name': 'plot_1', 'hide_input': False}),
           ('python echo=if a==5 then TRUE else FALSE', {
               'language': 'python', 'chunk_options': {'echo': 'if a==5 then TRUE else FALSE'}})]


@pytest.mark.parametrize('options,metadata', samples)
def test_parse_options(options, metadata):
    assert to_metadata(options) == metadata


@pytest.mark.skipif(sys.version_info < (3, 6), reason="unordered dict result in changes in chunk options")
@pytest.mark.parametrize('options,metadata', samples)
def test_build_options(options, metadata):
    assert to_chunk_options(metadata) == options


@pytest.mark.parametrize('options,metadata', samples)
def test_build_options_random_order(options, metadata):
    # Older python has no respect for order...
    # assert to_chunk_options(metadata) == options

    def split_and_strip(opt):
        set([o.strip() for o in opt.split(',')])

    assert split_and_strip(to_chunk_options(metadata)) == split_and_strip(options)
