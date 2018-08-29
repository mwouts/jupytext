"""Determine notebook or cell language"""

import re

_JUPYTER_LANGUAGES = ['R', 'bash', 'sh', 'python', 'python2', 'python3',
                      'javascript', 'js', 'perl']
_JUPYTER_LANGUAGES_RE = [re.compile(r"^%%{}\s*".format(lang))
                         for lang in _JUPYTER_LANGUAGES]


def is_code(cell):
    """Is the current code a code cell?"""
    if cell.cell_type == 'code':
        return True
    if cell.cell_type == 'raw' and 'active' in cell.metadata:
        return True
    return False


def get_default_language(nbk):
    """Return the default language of a notebook, and remove metadata
    'main_language' if that information is clear from notebook
    contents"""
    metadata = nbk.metadata

    default_language = (metadata.get('main_language') or
                        metadata.get('language_info', {})
                        .get('name', 'python').lower())

    if 'main_language' in metadata:
        # is 'main language' redundant with kernel info?
        if metadata['main_language'] is \
                metadata.get('language_info', {}).get('name'):
            del metadata['main_language']
        # is 'main language' redundant with cell language?
        elif metadata.get('language_info', {}).get('name') is None:
            languages = dict(python=0.5)
            for cell in nbk.cells:
                if cell.cell_type == 'code':
                    source = cell.source.splitlines()
                    language = default_language
                    if source:
                        for lang, pattern in zip(_JUPYTER_LANGUAGES,
                                                 _JUPYTER_LANGUAGES_RE):
                            if pattern.match(source[0]):
                                language = lang

                    languages[language] = 1 + languages.get(language, 0.0)

            cell_main_language = max(languages, key=languages.get)
            if metadata['main_language'] == cell_main_language:
                del metadata['main_language']

    return default_language


def find_main_language(metadata, cells):
    """
    Main language for the given collection of cells
    :param metadata:
    :param cells:
    :return:
    """
    main_language = (metadata.get('main_language') or
                     metadata.get('language_info', {}).get('name'))
    if main_language is None:
        languages = dict(python=0.5)
        for cell in cells:
            if cell.cell_type == 'code':
                language = cell['metadata']['language']
                languages[language] = languages.get(language, 0.0) + 1

        main_language = max(languages, key=languages.get)

        # save main language when not given by kernel
        if main_language is not \
                metadata.get('language_info', {}).get('name'):
            metadata['main_language'] = main_language

    # Remove 'language' meta data and add a magic if not main language
    for cell in cells:
        if is_code(cell):
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
