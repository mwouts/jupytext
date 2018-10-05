"""Determine notebook or cell language"""

import re

_JUPYTER_LANGUAGES = ['R', 'bash', 'sh', 'python', 'python2', 'python3',
                      'javascript', 'js', 'perl']
_JUPYTER_LANGUAGES_RE = [re.compile(r"^%%{}\s*".format(lang))
                         for lang in _JUPYTER_LANGUAGES]

_SCRIPT_EXTENSIONS = {'.py': {'language': 'python', 'comment': '#'},
                      '.R': {'language': 'R', 'comment': '#'},
                      '.jl': {'language': 'julia', 'comment': '#'},
                      '.cpp': {'language': 'c++', 'comment': '//'},
                      '.ss': {'language': 'scheme', 'comment': ';;'}}


def default_language_from_metadata_and_ext(notebook, ext):
    """Return the default language for a notebook that was read
    from the given file extension"""
    default_from_ext = _SCRIPT_EXTENSIONS.get(ext, {}).get('language', 'python')

    return (notebook.metadata.get('language_info', {}).get('name')
            or notebook.metadata.get('jupytext', {}).get('main_language') or default_from_ext)


def set_main_and_cell_language(metadata, cells, ext):
    """Set main language for the given collection of cells, and
    use magics for cells that use other languages"""
    default_from_ext = _SCRIPT_EXTENSIONS.get(ext, {}).get('language', 'python')
    main_language = (metadata.get('language_info', {}).get('name') or
                     metadata.get('jupytext', {}).get('main_language'))
    if main_language is None:
        languages = {default_from_ext: 0.5}
        for cell in cells:
            if 'language' in cell['metadata']:
                language = cell['metadata']['language']
                languages[language] = languages.get(language, 0.0) + 1

        main_language = max(languages, key=languages.get)

        # save main language when not kernel is set
        if 'name' not in metadata.get('language_info', {}):
            metadata.setdefault('jupytext', {})['main_language'] = main_language

    # Remove 'language' meta data and add a magic if not main language
    for cell in cells:
        if 'language' in cell['metadata']:
            language = cell['metadata']['language']
            del cell['metadata']['language']
            if language != main_language and \
                    language in _JUPYTER_LANGUAGES:
                cell['source'] = u'%%{}\n'.format(language) + cell['source']


def cell_language(source):
    """
    Return cell language
    :param source:
    :return:
    """
    if source:
        for lang, pattern in zip(_JUPYTER_LANGUAGES, _JUPYTER_LANGUAGES_RE):
            if pattern.match(source[0]):
                source.pop(0)
                return lang

    return None
