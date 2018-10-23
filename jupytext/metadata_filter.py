"""Notebook and cell metadata filtering"""


def parse_metadata_config(metadata_config, actual_keys, filtered_keys=None):
    """Return additional and excluded sets that correspond to a config of the form
    'entry_one,entry_two-negative_entry_one,negative_entry_two"""
    if metadata_config is True:
        metadata_config = 'all'
    elif metadata_config is False:
        metadata_config = '-all'
    elif metadata_config is None:
        metadata_config = ''

    if '-' in metadata_config:
        additional, excluded = metadata_config.split('-', 1)
        excluded = set(excluded.split(',')).difference({''})
        if not additional and 'all' not in excluded:
            additional = set(filtered_keys or actual_keys)
        else:
            additional = set(additional.split(',')).difference({''})
    else:
        additional = set(metadata_config.split(',')).difference({''})
        excluded = set()

    if 'all' in additional:
        additional = actual_keys
    if 'all' in excluded:
        excluded = actual_keys.difference(additional)

    return additional, excluded


def filter_metadata(metadata, user_metadata_config, default_metadata_config):
    """Filter the cell or notebook metadata, according to the user preference"""
    actual_keys = set(metadata.keys())
    default_positive, default_negative = parse_metadata_config(default_metadata_config, actual_keys)
    user_positive, user_negative = parse_metadata_config(
        user_metadata_config, actual_keys,
        actual_keys.intersection(default_positive).difference(default_negative))

    keep_keys = actual_keys.intersection(default_positive.difference(user_negative).union(user_positive)) \
        .difference(default_negative.difference(user_positive).union(user_negative))

    for key in actual_keys:
        if key not in keep_keys:
            del metadata[key]

    return metadata
