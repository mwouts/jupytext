"""Notebook and cell metadata filtering"""


def parse_metadata_config(metadata_config):
    """Return additional and excluded sets that correspond to a config of the form
    'entry_one,entry_two-negative_entry_one,negative_entry_two"""
    if not metadata_config:
        return set(), set()

    if isinstance(metadata_config, list):
        return set(metadata_config), set()

    if isinstance(metadata_config, tuple):
        additional, excluded = metadata_config
        return set(additional), set(excluded)

    if '-' in metadata_config:
        additional, excluded = metadata_config.split('-', 1)
        additional = additional.split(',')
        excluded = excluded.split(',')
        return set(additional), set(excluded)

    additional = metadata_config.split(',')
    return set(additional), set()


def filter_metadata(metadata, user_metadata_config, default_metadata_config):
    """Filter the cell or notebook metadata, according to the user preference"""
    if user_metadata_config is True:
        return metadata

    if user_metadata_config is False:
        return {}

    actual_keys = set(metadata.keys())
    default_positive, default_negative = parse_metadata_config(default_metadata_config)
    user_positive, user_negative = parse_metadata_config(user_metadata_config)

    if not default_positive:
        keep_keys = actual_keys.difference(default_negative.difference(user_positive)).difference(user_negative)
    else:
        keep_keys = actual_keys.intersection(default_positive.union(user_positive)).difference(user_negative)

    for key in actual_keys:
        if key not in keep_keys:
            del metadata[key]

    return metadata
