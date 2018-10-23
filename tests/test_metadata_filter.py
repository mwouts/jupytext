from jupytext.metadata_filter import filter_metadata


def to_dict(keys):
    return {key: None for key in keys}


def test_metadata_filter_default():
    assert filter_metadata(to_dict(['technical', 'user', 'preserve']), None, '-technical'
                           ) == to_dict(['user', 'preserve'])
    assert filter_metadata(to_dict(['technical', 'user', 'preserve']), None, 'preserve-all'
                           ) == to_dict(['preserve'])


def test_metadata_filter_user_plus_default():
    assert filter_metadata(to_dict(['technical', 'user', 'preserve']), '-user', '-technical'
                           ) == to_dict(['preserve'])
    assert filter_metadata(to_dict(['technical', 'user', 'preserve']), 'all-user', '-technical'
                           ) == to_dict(['preserve', 'technical'])
    assert filter_metadata(to_dict(['technical', 'user', 'preserve']), 'user', 'preserve-all'
                           ) == to_dict(['user', 'preserve'])


def test_metadata_filter_user_overrides_default():
    assert filter_metadata(to_dict(['technical', 'user', 'preserve']), 'all-user', '-technical'
                           ) == to_dict(['technical', 'preserve'])
    assert filter_metadata(to_dict(['technical', 'user', 'preserve']), 'user-all', 'preserve'
                           ) == to_dict(['user'])
