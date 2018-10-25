"""Notebook and cell metadata filtering"""


def metadata_filter_as_dict(metadata_config):
    """Return the metadata filter represented as either None (no filter),
    or a dictionary with at most two keys: 'additional' and 'excluded',
    which contain either a list of metadata names, or the string 'all'"""

    if metadata_config is None:
        return {}

    if metadata_config is True:
        return {'additional': 'all'}

    if metadata_config is False:
        return {'excluded': 'all'}

    if isinstance(metadata_config, dict):
        assert set(metadata_config) <= set(['additional', 'excluded'])
        return metadata_config

    metadata_keys = metadata_config.split(',')

    metadata_config = {}

    for key in metadata_keys:
        key = key.strip()
        if key.startswith('-'):
            metadata_config.setdefault('excluded', []).append(key[1:].strip())
        elif key.startswith('+'):
            metadata_config.setdefault('additional', []).append(key[1:].strip())
        else:
            metadata_config.setdefault('additional', []).append(key)

    for section in metadata_config:
        if 'all' in metadata_config[section]:
            metadata_config[section] = 'all'
        else:
            metadata_config[section] = [key for key in metadata_config[section] if key]

    return metadata_config


def apply_metadata_filter(metadata_config, actual_keys, filtered_keys=None):
    """Apply the filter and replace 'all' with the actual or filtered keys"""

    metadata_config = metadata_filter_as_dict(metadata_config)
    additional = metadata_config.get('additional') or set()
    excluded = metadata_config.get('excluded') or set()

    if not additional and excluded and excluded != 'all':
        additional = set(filtered_keys or actual_keys).difference(excluded)

    if additional == 'all':
        additional = actual_keys

    if excluded == 'all':
        excluded = set(actual_keys).difference(additional)

    return set(additional), set(excluded)


def filter_metadata(metadata, user_metadata_config, default_metadata_config):
    """Filter the cell or notebook metadata, according to the user preference"""
    actual_keys = set(metadata.keys())
    default_positive, default_negative = apply_metadata_filter(default_metadata_config, actual_keys)
    user_positive, user_negative = apply_metadata_filter(
        user_metadata_config, actual_keys,
        actual_keys.intersection(default_positive).difference(default_negative))

    keep_keys = actual_keys.intersection(default_positive.difference(user_negative).union(user_positive)) \
        .difference(default_negative.difference(user_positive).union(user_negative))

    for key in actual_keys:
        if key not in keep_keys:
            del metadata[key]

    return metadata
