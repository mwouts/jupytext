from nbrmd.chunk_options import to_metadata, to_chunk_options
import pytest

samples = [('r plot_1, dpi=72, fig.path="fig_path/"', {
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


@pytest.mark.parametrize('options,metadata', samples)
def test_build_options(options, metadata):
    assert to_chunk_options(metadata) == options
