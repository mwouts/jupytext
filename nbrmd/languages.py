import re

_jupyter_languages = ['R', 'bash', 'sh', 'python', 'python2', 'python3',
                      'javascript', 'js', 'perl']
_jupyter_languages_re = [re.compile(r"^%%{}\s*".format(lang))
                         for lang in _jupyter_languages]


def get_default_language(nb):
    """Return the default language of a notebook, and remove metadata
    'main_language' if that information is clear from notebook
    contents"""
    metadata = nb.metadata

    default_language = (
            metadata.get('main_language') or
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
            for c in nb.cells:
                if c.cell_type == 'code':
                    input = c.source.splitlines()
                    language = default_language
                    if len(input):
                        for lang, pattern in zip(_jupyter_languages,
                                                 _jupyter_languages_re):
                            if pattern.match(input[0]):
                                language = lang

                    languages[language] = 1 + languages.get(
                        language, 0.0)

            cell_main_language = max(languages, key=languages.get)
            if metadata['main_language'] == cell_main_language:
                del metadata['main_language']

    return default_language


def find_main_language(metadata, cells):
    main_language = (metadata.get('main_language') or
                     metadata.get('language_info', {}).get('name'))
    if main_language is None:
        languages = dict(python=0.5)
        for c in cells:
            if c['cell_type'] == 'code':
                language = c['metadata']['language']
                languages[language] = languages.get(language, 0.0) + 1

        main_language = max(languages, key=languages.get)

        # save main language when not given by kernel
        if main_language is not \
                metadata.get('language_info', {}).get('name'):
            metadata['main_language'] = main_language

    # Remove 'language' meta data and add a magic if not main language
    for c in cells:
        if c['cell_type'] == 'code':
            language = c['metadata']['language']
            del c['metadata']['language']
            if language != main_language and \
                    language in _jupyter_languages:
                c['source'] = u'%%{}\n'.format(language) + c['source']


def cell_language(source):
    if len(source):
        for lang, pattern in zip(_jupyter_languages, _jupyter_languages_re):
            if pattern.match(source[0]):
                source.pop(0)
                return lang
