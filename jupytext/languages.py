"""Determine notebook or cell language"""

# Jupyter magic commands that are also languages
_JUPYTER_LANGUAGES = ['R', 'bash', 'sh', 'python', 'python2', 'python3', 'javascript', 'js', 'perl',
                      'html', 'latex', 'markdown', 'pypy', 'ruby', 'script', 'svg',
                      'matlab', 'octave', 'idl', 'robotframework', 'spark', 'sql']

# Supported file extensions (and languages)
# Please add more languages here (and add a few tests) - see CONTRIBUTING.md
_SCRIPT_EXTENSIONS = {'.py': {'language': 'python', 'comment': '#'},
                      '.R': {'language': 'R', 'comment': '#'},
                      '.r': {'language': 'R', 'comment': '#'},
                      '.jl': {'language': 'julia', 'comment': '#'},
                      '.cpp': {'language': 'c++', 'comment': '//'},
                      '.ss': {'language': 'scheme', 'comment': ';;'},
                      '.clj': {'language': 'clojure', 'comment': ';;'},
                      '.scm': {'language': 'scheme', 'comment': ';;'},
                      '.sh': {'language': 'bash', 'comment': '#'},
                      '.ps1': {'language': 'powershell', 'comment': '#'},
                      '.q': {'language': 'q', 'comment': '/'},
                      '.m': {'language': 'matlab', 'comment': '%'},
                      '.pro': {'language': 'idl', 'comment': ';'},
                      '.js': {'language': 'javascript', 'comment': '//'},
                      '.ts': {'language': 'typescript', 'comment': '//'},
                      '.scala': {'language': 'scala', 'comment': '//'},
                      '.rs': {'language': 'rust', 'comment': '//'},
                      '.robot': {'language': 'robotframework', 'comment': '#'}}

_COMMENT_CHARS = [_SCRIPT_EXTENSIONS[ext]['comment'] for ext in _SCRIPT_EXTENSIONS if
                  _SCRIPT_EXTENSIONS[ext]['comment'] != '#']

_COMMENT = {_SCRIPT_EXTENSIONS[ext]['language']: _SCRIPT_EXTENSIONS[ext]['comment'] for ext in _SCRIPT_EXTENSIONS}
_JUPYTER_LANGUAGES = set(_JUPYTER_LANGUAGES).union(_COMMENT.keys())
_JUPYTER_LANGUAGES_LOWER_AND_UPPER = _JUPYTER_LANGUAGES.union({str.upper(lang) for lang in _JUPYTER_LANGUAGES})


def default_language_from_metadata_and_ext(metadata, ext):
    """Return the default language given the notebook metadata, and a file extension"""
    default_from_ext = _SCRIPT_EXTENSIONS.get(ext, {}).get('language')

    language = (metadata.get('jupytext', {}).get('main_language')
                or metadata.get('kernelspec', {}).get('language')
                or default_from_ext)

    if language is None or language == 'R':
        return language

    if language.startswith('C++'):
        return 'c++'

    return language.lower()


def same_language(kernel_language, language):
    """Are those the same language?"""
    if kernel_language == language:
        return True
    if kernel_language.lower() == language:
        return True
    if kernel_language.startswith('C++') and language == 'c++':
        return True
    if kernel_language == 'octave' and language == 'matlab':
        return True
    return False


def set_main_and_cell_language(metadata, cells, ext):
    """Set main language for the given collection of cells, and
    use magics for cells that use other languages"""
    main_language = default_language_from_metadata_and_ext(metadata, ext)

    if main_language is None:
        languages = {'python': 0.5}
        for cell in cells:
            if 'language' in cell['metadata']:
                language = cell['metadata']['language']
                languages[language] = languages.get(language, 0.0) + 1

        main_language = max(languages, key=languages.get)

    # save main language when no kernel is set
    if 'language' not in metadata.get('kernelspec', {}) and cells:
        metadata.setdefault('jupytext', {})['main_language'] = main_language

    # Remove 'language' meta data and add a magic if not main language
    for cell in cells:
        if 'language' in cell['metadata']:
            language = cell['metadata'].pop('language')
            if language != main_language and language in _JUPYTER_LANGUAGES:
                if 'magic_args' in cell['metadata']:
                    magic_args = cell['metadata'].pop('magic_args')
                    cell['source'] = u'%%{} {}\n'.format(language, magic_args) + cell['source']
                else:
                    cell['source'] = u'%%{}\n'.format(language) + cell['source']


def cell_language(source):
    """Return cell language and language options, if any"""
    if source:
        line = source[0]
        if line.startswith('%%'):
            magic = line[2:]
            if ' ' in magic:
                lang, magic_args = magic.split(' ', 1)
            else:
                lang = magic
                magic_args = ''

            if lang in _JUPYTER_LANGUAGES:
                source.pop(0)
                return lang, magic_args

    return None, None


def comment_lines(lines, prefix):
    """Return commented lines"""
    if not prefix:
        return lines
    return [prefix + ' ' + line if line else prefix for line in lines]
