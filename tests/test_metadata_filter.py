import pytest
from jupytext.metadata_filter import filter_metadata, metadata_filter_as_dict


def to_dict(keys):
    return {key: None for key in keys}


@pytest.mark.parametrize('metadata_filter_string,metadata_filter_dict',
                         [('all, -widgets,-varInspector',
                           {'additional': 'all', 'excluded': ['widgets', 'varInspector']}),
                          ('toc', {'additional': ['toc']}),
                          ('+ toc', {'additional': ['toc']}),
                          ('preserve,-all', {'additional': ['preserve'], 'excluded': 'all'}),
                          ('ExecuteTime, autoscroll, -hide_output',
                           {'additional': ['ExecuteTime', 'autoscroll'], 'excluded': ['hide_output']})])
def test_string_to_dict_conversion(metadata_filter_string, metadata_filter_dict):
    assert metadata_filter_as_dict(metadata_filter_string) == metadata_filter_dict


def test_metadata_filter_as_dict():
    assert metadata_filter_as_dict(True) == metadata_filter_as_dict('all')
    assert metadata_filter_as_dict(False) == metadata_filter_as_dict('-all')
    assert metadata_filter_as_dict({'excluded': 'all'}) == metadata_filter_as_dict('-all')


def test_metadata_filter_default():
    assert filter_metadata(to_dict(['technical', 'user', 'preserve']), None, '-technical'
                           ) == to_dict(['user', 'preserve'])
    assert filter_metadata(to_dict(['technical', 'user', 'preserve']), None, 'preserve,-all'
                           ) == to_dict(['preserve'])


def test_metadata_filter_user_plus_default():
    assert filter_metadata(to_dict(['technical', 'user', 'preserve']), '-user', '-technical'
                           ) == to_dict(['preserve'])
    assert filter_metadata(to_dict(['technical', 'user', 'preserve']), 'all,-user', '-technical'
                           ) == to_dict(['preserve', 'technical'])
    assert filter_metadata(to_dict(['technical', 'user', 'preserve']), 'user', 'preserve,-all'
                           ) == to_dict(['user', 'preserve'])


def test_metadata_filter_user_overrides_default():
    assert filter_metadata(to_dict(['technical', 'user', 'preserve']), 'all,-user', '-technical'
                           ) == to_dict(['technical', 'preserve'])
    assert filter_metadata(to_dict(['technical', 'user', 'preserve']), 'user,-all', 'preserve'
                           ) == to_dict(['user'])
