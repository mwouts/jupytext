"""
Convert between text notebook metadata and jupyter cell metadata.

See also https://ipython.org/ipython-doc/3/notebook/nbformat.html#cell-metadata

metadata.hide_input and metadata.hide_output are documented here:
http://jupyter-contrib-nbextensions.readthedocs.io/en/latest/nbextensions/runtools/readme.html

TODO: Update this if a standard gets defined at
https://github.com/jupyter/notebook/issues/3700

Note: Nteract uses "outputHidden" and "inputHidden". We may want to switch
to those.
"""

import ast
import json
import re

from .languages import _JUPYTER_LANGUAGES

try:
    unicode  # Python 2
except NameError:
    unicode = str  # Python 3

_BOOLEAN_OPTIONS_DICTIONARY = [('hide_input', 'echo', True),
                               ('hide_output', 'include', True)]
_IGNORE_METADATA = [
    # Frequent cell metadata that should not enter the text representation
    # (these metadata are preserved in the paired Jupyter notebook).
    'autoscroll', 'collapsed', 'scrolled', 'trusted', 'ExecuteTime',
    # Pre-jupytext metadata
    'skipline', 'noskipline',
    # Jupytext metadata
    'lines_to_next_cell', 'lines_to_end_of_cell_marker']
_PERCENT_CELL = re.compile(
    r'(# |#)%%([^\{\[]*)(|\[raw\]|\[markdown\])([^\{\[]*)(|\{.*\})\s*$')


def _r_logical_values(pybool):
    return 'TRUE' if pybool else 'FALSE'


class RLogicalValueError(Exception):
    """Incorrect value for R boolean"""
    pass


class RMarkdownOptionParsingError(Exception):
    """Error when parsing Rmd cell options"""
    pass


def _py_logical_values(rbool):
    if rbool in ['TRUE', 'T']:
        return True
    if rbool in ['FALSE', 'F']:
        return False
    raise RLogicalValueError


def metadata_to_rmd_options(language, metadata):
    """
    Convert language and metadata information to their rmd representation
    :param language:
    :param metadata:
    :return:
    """
    options = (language or 'R').lower()
    metadata = filter_metadata(metadata)
    if 'name' in metadata:
        options += ' ' + metadata['name'] + ','
        del metadata['name']
    for jupyter_option, rmd_option, rev in _BOOLEAN_OPTIONS_DICTIONARY:
        if jupyter_option in metadata:
            options += ' {}={},'.format(
                rmd_option, _r_logical_values(metadata[jupyter_option] != rev))
            del metadata[jupyter_option]
    for opt_name in metadata:
        opt_value = metadata[opt_name]
        opt_name = opt_name.strip()
        if opt_name == 'active':
            options += ' {}="{}",'.format(opt_name, str(opt_value))
        elif isinstance(opt_value, bool):
            options += ' {}={},'.format(
                opt_name, 'TRUE' if opt_value else 'FALSE')
        elif isinstance(opt_value, list):
            options += ' {}={},'.format(
                opt_name, 'c({})'.format(
                    ', '.join(['"{}"'.format(str(v)) for v in opt_value])))
        else:
            options += ' {}={},'.format(opt_name, str(opt_value))
    if not language:
        options = options[2:]
    return options.strip(',').strip()


def update_metadata_from_rmd_options(name, value, metadata):
    """
    Update metadata using the _BOOLEAN_OPTIONS_DICTIONARY mapping
    :param name: option name
    :param value: option value
    :param metadata:
    :return:
    """
    for jupyter_option, rmd_option, rev in _BOOLEAN_OPTIONS_DICTIONARY:
        if name == rmd_option:
            try:
                metadata[jupyter_option] = _py_logical_values(value) != rev
                return True
            except RLogicalValueError:
                pass
    return False


class ParsingContext:
    """
    Class for determining where to split rmd options
    """
    parenthesis_count = 0
    curly_bracket_count = 0
    square_bracket_count = 0
    in_single_quote = False
    in_double_quote = False

    def __init__(self, line):
        self.line = line

    def in_global_expression(self):
        """Currently inside an expression"""
        return (self.parenthesis_count == 0 and self.curly_bracket_count == 0
                and self.square_bracket_count == 0
                and not self.in_single_quote and not self.in_double_quote)

    def count_special_chars(self, char, prev_char):
        """Update parenthesis counters"""
        if char == '(':
            self.parenthesis_count += 1
        elif char == ')':
            self.parenthesis_count -= 1
            if self.parenthesis_count < 0:
                raise RMarkdownOptionParsingError(
                    'Option line "{}" has too many '
                    'closing parentheses'.format(self.line))
        elif char == '{':
            self.curly_bracket_count += 1
        elif char == '}':
            self.curly_bracket_count -= 1
            if self.curly_bracket_count < 0:
                raise RMarkdownOptionParsingError(
                    'Option line "{}" has too many '
                    'closing curly brackets'.format(self.line))
        elif char == '[':
            self.square_bracket_count += 1
        elif char == ']':
            self.square_bracket_count -= 1
            if self.square_bracket_count < 0:
                raise RMarkdownOptionParsingError(
                    'Option line "{}" has too many '
                    'closing square brackets'.format(self.line))
        elif char == "'" and prev_char != '\\':
            self.in_single_quote = not self.in_single_quote
        elif char == '"' and prev_char != '\\':
            self.in_double_quote = not self.in_double_quote


def parse_rmd_options(line):
    """
    Given a R markdown option line, returns a list of pairs name,value
    :param line:
    :return:
    """
    parsing_context = ParsingContext(line)

    result = []
    prev_char = ''

    name = ''
    value = ''

    for char in ',' + line + ',':
        if parsing_context.in_global_expression():
            if char == ',':
                if name != '' or value != '':
                    if result and name == '':
                        raise RMarkdownOptionParsingError(
                            'Option line "{}" has no name for '
                            'option value {}'.format(line, value))
                    result.append((name.strip(), value.strip()))
                    name = ''
                    value = ''
            elif char == '=':
                if name == '':
                    name = value
                    value = ''
                else:
                    value += char
            else:
                parsing_context.count_special_chars(char, prev_char)
                value += char
        else:
            parsing_context.count_special_chars(char, prev_char)
            value += char
        prev_char = char

    if not parsing_context.in_global_expression():
        raise RMarkdownOptionParsingError(
            'Option line "{}" is not properly terminated'.format(line))

    return result


def rmd_options_to_metadata(options):
    """
    Parse rmd options and return a metadata dictionary
    :param options:
    :return:
    """
    options = re.split(r'\s|,', options, 1)
    if len(options) == 1:
        language = options[0]
        chunk_options = []
    else:
        language, others = options
        language = language.rstrip(' ,')
        others = others.lstrip(' ,')
        chunk_options = parse_rmd_options(others)

    language = 'R' if language == 'r' else language
    metadata = {}
    for i, opt in enumerate(chunk_options):
        name, value = opt
        if i == 0 and name == '':
            metadata['name'] = value
            continue
        else:
            if update_metadata_from_rmd_options(name, value, metadata):
                continue
            if name == 'active':
                metadata[name] = value.replace('"', '').replace("'", '')
                continue
            try:
                metadata[name] = _py_logical_values(value)
                continue
            except RLogicalValueError:
                metadata[name] = value

    for name in metadata:
        try_eval_metadata(metadata, name)

    if ('active' in metadata or metadata.get('run_control', {}).get('frozen') is True) and 'eval' in metadata:
        del metadata['eval']

    return language, metadata


def md_options_to_metadata(options):
    """Parse markdown options and return language and metadata (cell name)"""
    language = None
    name = None

    options = [opt for opt in options.split(' ') if opt != '']
    if len(options) >= 2:
        language, name = options[:2]
    elif options:
        language = options[0]

    if language:
        for lang in _JUPYTER_LANGUAGES + ['julia', 'scheme', 'c++']:
            if language.lower() == lang.lower():
                if name:
                    return lang, {'name': name}
                return lang, {}

        return None, {'name': language}

    return None, {}


def try_eval_metadata(metadata, name):
    """Evaluate given metadata to a python object, if possible"""
    value = metadata[name]
    if not isinstance(value, (str, unicode)):
        return
    if value.startswith('"') or value.startswith("'"):
        return
    if value.startswith('c(') and value.endswith(')'):
        value = '[' + value[2:-1] + ']'
    elif value.startswith('list(') and value.endswith(')'):
        value = '[' + value[5:-1] + ']'
    try:
        metadata[name] = ast.literal_eval(value)
    except (SyntaxError, ValueError):
        return


def json_options_to_metadata(options, add_brackets=True):
    """Read metadata from its json representation"""
    try:
        options = json.loads('{' + options + '}' if add_brackets else options)
        return options
    except ValueError:
        return {}


def filter_metadata(metadata):
    """Filter technical metadata"""
    return {k: metadata[k] for k in metadata if k not in _IGNORE_METADATA}


def metadata_to_json_options(metadata):
    """Represent metadata as json text"""
    return json.dumps(metadata)


def is_active(ext, metadata):
    """Is the cell active for the given file extension?"""
    if metadata.get('run_control', {}).get('frozen') is True:
        return False
    if 'active' not in metadata:
        return True
    return ext.replace('.', '') in re.split('\\.|,', metadata['active'])


def double_percent_options_to_metadata(options):
    """Parse double percent options"""
    matches = _PERCENT_CELL.findall('# %%' + options)
    if matches == []: ## didn't match with options
        matches = _PERCENT_CELL.findall('# %%')
        ## assume a code cell, with extra stuff
        if matches == []: ## didn't match at all
            return {}
        else:
            ## Put rest of line in title metadata:
            matches = list(matches[0])
            matches[1] = options
    else:
        matches = matches[0]
    # Fifth match are JSON metadata
    if matches[4]:
        metadata = json_options_to_metadata(matches[4], add_brackets=False)
    else:
        metadata = {}

    # Third match is cell type
    cell_type = matches[2]
    if cell_type:
        metadata['cell_type'] = cell_type[1:-1]

    # Second and fourth match are description
    title = [matches[i].strip() for i in [1, 3]]
    title = [part for part in title if part]
    if title:
        title = ' '.join(title)
        cell_depth = 0
        while title.startswith('%'):
            cell_depth += 1
            title = title[1:]

        if cell_depth:
            metadata['cell_depth'] = cell_depth
        metadata['title'] = title.strip()

    return metadata


def metadata_to_double_percent_options(metadata):
    """Metadata to double percent lines"""
    options = []
    if 'cell_depth' in metadata:
        options.append('%' * metadata.pop('cell_depth'))
    if 'title' in metadata:
        options.append(metadata.pop('title'))
    if 'cell_type' in metadata:
        options.append('[{}]'.format(metadata.pop('cell_type')))
    if metadata:
        options.append(metadata_to_json_options(metadata))
    return ' '.join(options)
