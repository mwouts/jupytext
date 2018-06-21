def to_chunk_options(metadata):
    options = metadata['language'].lower()
    if 'name' in metadata:
        options += ' ' + metadata['name'] + ','
    if 'hide_input' in metadata:
        options += ' echo=' + ('FALSE' if metadata['hide_input'] else 'TRUE') + ','
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
            if name == 'echo':
                if value == 'TRUE':
                    metadata['hide_input'] = False
                    continue
                if value == 'FALSE':
                    metadata['hide_input'] = True
                    continue
            metadata['chunk_options'][name] = value
    if len(metadata['chunk_options']) == 0:
        del metadata['chunk_options']
    return metadata
