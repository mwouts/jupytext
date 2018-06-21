"""
Convert between R markdown chunk options and jupyter cell metadata.

metadata.hide_input and metadata.hide_output are documented here:
http://jupyter-contrib-nbextensions.readthedocs.io/en/latest/nbextensions/runtools/readme.html
"""

_boolean_options_dictionary = [('hide_input', 'echo', True), ('hide_output', 'include', True)]
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


def to_chunk_options(metadata):
    options = metadata['language'].lower()
    if 'name' in metadata:
        options += ' ' + metadata['name'] + ','
    for jo, ro, rev in _boolean_options_dictionary:
        if jo in metadata:
            options += ' {}={},'.format(ro, _r_logical_values(metadata[jo] != rev))
    chunk_options = metadata.get('chunk_options', {})
    for co_name in chunk_options:
        co_value = chunk_options[co_name]
        co_name = co_name.strip()
        if co_value is None:
            options += ' {},'.format(co_name)
        else:
            options += ' {}={},'.format(co_name, co_value)
    return options.strip(',')


def to_metadata(options):
    options = options.split(' ', 1)
    if len(options)==1:
        language = options[0]
        chunk_options = []
    else:
        language, others = options
        chunk_options = others.split(',')
    metadata = {'language': 'R' if language == 'r' else language}
    metadata['chunk_options'] = {}
    for i, co in enumerate(chunk_options):
        co = co.split('=', 1)
        if len(co) == 1:
            name = co[0].strip(' ')
            if i == 0:
                metadata['name'] = name
                continue
            metadata['chunk_options'][name] = None
        else:
            name, value = co
            name = name.strip()
            for jo, ro, rev in _boolean_options_dictionary:
                if name==ro:
                    try:
                        metadata[jo] = _py_logical_values(value) != rev
                        continue
                    except RLogicalValueError:
                        pass
            metadata['chunk_options'][name] = value
    if len(metadata['chunk_options']) == 0:
        del metadata['chunk_options']
    return metadata
