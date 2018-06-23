"""
Convert between R markdown chunk options and jupyter cell metadata.

metadata.hide_input and metadata.hide_output are documented here:
http://jupyter-contrib-nbextensions.readthedocs.io/en/latest/nbextensions/runtools/readme.html

TODO: Update this if a standard gets defined at https://github.com/jupyter/notebook/issues/3700
"""

_boolean_options_dictionary = [('hide_input', 'echo', True), ('hide_output', 'include', True)]
_ignore_metadata = ['collapsed', 'autoscroll', 'deletable', 'format', 'trusted', 'tags']


def _r_logical_values(bool):
    return 'TRUE' if bool else 'FALSE'


class RLogicalValueError(Exception):
    pass


def _py_logical_values(rbool):
    if rbool in ['TRUE', 'T']:
        return True
    if rbool in ['FALSE', 'F']:
        return False
    raise RLogicalValueError


def to_chunk_options(language, metadata):
    options = language.lower()
    if 'name' in metadata:
        options += ' ' + metadata['name'] + ','
        del metadata['name']
    for jo, ro, rev in _boolean_options_dictionary:
        if jo in metadata:
            options += ' {}={},'.format(ro, _r_logical_values(metadata[jo] != rev))
            del metadata[jo]
    for co_name in metadata:
        co_value = metadata[co_name]
        co_name = co_name.strip()
        if co_name in _ignore_metadata:
            continue
        if co_value is None:
            options += ' {},'.format(co_name)
        elif isinstance(co_value, str):
            options += ' {}={},'.format(co_name, co_value)
        elif isinstance(co_value, bool):
            options += ' {}={},'.format(co_name, 'TRUE' if co_value else 'FALSE')
        else:
            options += ' {}="{}",'.format(co_name, str(co_value))
    return options.strip(',')


def update_metadata_using_dictionary(name, value, metadata):
    for jo, ro, rev in _boolean_options_dictionary:
        if name == ro:
            try:
                metadata[jo] = _py_logical_values(value) != rev
                return True
            except RLogicalValueError:
                pass
    return False


def to_metadata(options):
    options = options.split(' ', 1)
    if len(options) == 1:
        language = options[0]
        chunk_options = []
    else:
        language, others = options
        chunk_options = others.split(',')
    language = 'R' if language == 'r' else language
    metadata = {}
    for i, co in enumerate(chunk_options):
        co = co.split('=', 1)
        if len(co) == 1:
            name = co[0].strip(' ')
            if i == 0:
                metadata['name'] = name
                continue
            metadata[name] = None
        else:
            name, value = co
            name = name.strip()

            if update_metadata_using_dictionary(name, value, metadata):
                continue
            try:
                metadata[name] = _py_logical_values(value)
                continue
            except RLogicalValueError:
                metadata[name] = value
    return language, metadata
