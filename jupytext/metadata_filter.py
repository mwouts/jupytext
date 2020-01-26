"""Notebook and cell metadata filtering"""

from copy import copy
from .cell_metadata import _JUPYTEXT_CELL_METADATA

_DEFAULT_NOTEBOOK_METADATA = ','.join([
    # Preserve Jupytext section
    'jupytext',
    # Preserve kernel specs
    'kernelspec',
    # Kernel_info found in Nteract notebooks
    'kernel_info'])


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
            metadata_config[section] = [k for k in metadata_config[section] if k]

    return metadata_config


def metadata_filter_as_string(metadata_filter):
    """Convert a filter, represented as a dictionary with 'additional' and 'excluded' entries, to a string"""
    if not isinstance(metadata_filter, dict):
        return metadata_filter

    additional = metadata_filter.get('additional', [])
    if additional == 'all':
        entries = ['all']
    else:
        entries = [key for key in additional if key not in _JUPYTEXT_CELL_METADATA]

    excluded = metadata_filter.get('excluded', [])
    if excluded == 'all':
        entries.append('-all')
    else:
        entries.extend(['-' + e for e in excluded])

    return ','.join(entries)


def update_metadata_filters(metadata, jupyter_md, cell_metadata):
    """Update or set the notebook and cell metadata filters"""

    cell_metadata = [m for m in cell_metadata if m not in ['language', 'magic_args']]

    if 'cell_metadata_filter' in metadata.get('jupytext', {}):
        metadata_filter = metadata_filter_as_dict(metadata.get('jupytext', {})['cell_metadata_filter'])
        if isinstance(metadata_filter.get('excluded'), list):
            metadata_filter['excluded'] = [key for key in metadata_filter['excluded'] if key not in cell_metadata]
        metadata_filter.setdefault('additional', [])
        if isinstance(metadata_filter.get('additional'), list):
            for key in cell_metadata:
                if key not in metadata_filter['additional']:
                    metadata_filter['additional'].append(key)
        metadata.setdefault('jupytext', {})['cell_metadata_filter'] = metadata_filter_as_string(metadata_filter)

    if not jupyter_md:
        # Set a metadata filter equal to the current metadata in script
        cell_metadata = {'additional': cell_metadata, 'excluded': 'all'}
        metadata.setdefault('jupytext', {})['notebook_metadata_filter'] = '-all'
        metadata.setdefault('jupytext', {})['cell_metadata_filter'] = metadata_filter_as_string(cell_metadata)
    else:
        # Update the notebook metadata filter to include existing entries 376
        nb_md_filter = metadata.get('jupytext', {}).get('notebook_metadata_filter', '').split(',')
        nb_md_filter = [key for key in nb_md_filter if key]
        if 'all' in nb_md_filter or '-all' in nb_md_filter:
            return
        for key in metadata:
            if key in _DEFAULT_NOTEBOOK_METADATA or key in nb_md_filter or ('-' + key) in nb_md_filter:
                continue
            nb_md_filter.append(key)
        if nb_md_filter:
            metadata.setdefault('jupytext', {})['notebook_metadata_filter'] = ','.join(nb_md_filter)


def filter_metadata(metadata, user_filter, default_filter):
    """Filter the cell or notebook metadata, according to the user preference"""
    default_filter = metadata_filter_as_dict(default_filter) or {}
    user_filter = metadata_filter_as_dict(user_filter) or {}

    for key in ['additional', 'excluded']:
        default_filter.setdefault(key, [])
        user_filter.setdefault(key, [])

    if user_filter.get('excluded') == 'all':
        default_filter['additional'] = []
    if user_filter.get('additional') == 'all':
        default_filter['excluded'] = []

    # notebook default filter = only few metadata
    if default_filter.get('additional'):
        if user_filter.get('additional') == 'all':
            return subset_metadata(metadata, exclude=user_filter.get('excluded'))
        return subset_metadata(metadata,
                               keep_only=set(user_filter.get('additional')).union(default_filter.get('additional')),
                               exclude=user_filter.get('excluded'))

    # cell default filter = all metadata but removed ones
    if user_filter.get('excluded') == 'all':
        return subset_metadata(metadata, keep_only=user_filter.get('additional'))

    return subset_metadata(metadata, exclude=set(user_filter.get('excluded'))
                           .union(set(default_filter.get('excluded')).difference(user_filter.get('additional'))))


def subset_metadata(metadata, keep_only=None, exclude=None):
    """Filter the metadata by reference, according to keep_only and then to exclude"""
    if keep_only is not None:
        for key in set(metadata.keys()):
            if key not in keep_only:
                metadata.pop(key)

    if exclude is not None:
        for key in exclude:
            if key in set(metadata.keys()):
                metadata.pop(key)

    return metadata


def restore_filtered_metadata(filtered_metadata, unfiltered_metadata, user_filter, default_filter):
    """Update the filtered metadata with the part of the unfiltered one that matches the filter"""
    filtered_unfiltered_metadata = copy(unfiltered_metadata)
    filter_metadata(filtered_unfiltered_metadata, user_filter, default_filter)

    for key in unfiltered_metadata:
        if key not in filtered_unfiltered_metadata:
            filtered_metadata[key] = unfiltered_metadata[key]
