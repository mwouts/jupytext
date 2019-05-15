"""
Convert between text notebook metadata and jupyter cell metadata.

Standard cell metadata are documented here:
See also https://ipython.org/ipython-doc/3/notebook/nbformat.html#cell-metadata
"""

import ast
import re
from json import loads, dumps

try:
    from json import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError

from .languages import _JUPYTER_LANGUAGES

try:
    unicode  # Python 2
except NameError:
    unicode = str  # Python 3

# Map R Markdown's "echo" and "include" to "hide_input" and "hide_output", that are understood by the `runtools`
# extension for Jupyter notebook, and by nbconvert (use the `hide_input_output.tpl` template).
# See http://jupyter-contrib-nbextensions.readthedocs.io/en/latest/nbextensions/runtools/readme.html
_BOOLEAN_OPTIONS_DICTIONARY = [('hide_input', 'echo', True),
                               ('hide_output', 'include', True)]
_JUPYTEXT_CELL_METADATA = [
    # Pre-jupytext metadata
    'skipline', 'noskipline',
    # Jupytext metadata
    'cell_marker', 'lines_to_next_cell', 'lines_to_end_of_cell_marker']
_IGNORE_CELL_METADATA = ','.join('-{}'.format(name) for name in [
    # Frequent cell metadata that should not enter the text representation
    # (these metadata are preserved in the paired Jupyter notebook).
    'autoscroll', 'collapsed', 'scrolled', 'trusted', 'ExecuteTime'] +
                                 _JUPYTEXT_CELL_METADATA)
_PERCENT_CELL = re.compile(
    r'(# |#)%%([^\{\[]*)(|\[raw\]|\[markdown\])([^\{\[]*)(|\{.*\})\s*$')


def _r_logical_values(pybool):
    return 'TRUE' if pybool else 'FALSE'


class RLogicalValueError(Exception):
    """Incorrect value for R boolean"""


class RMarkdownOptionParsingError(Exception):
    """Error when parsing Rmd cell options"""


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
            try:
                metadata[name] = _py_logical_values(value)
                continue
            except RLogicalValueError:
                metadata[name] = value

    for name in metadata:
        try_eval_metadata(metadata, name)

    if 'eval' in metadata and not is_active('.Rmd', metadata):
        del metadata['eval']

    return metadata.get('language') or language, metadata


def metadata_to_md_options(metadata):
    """Encode {'class':None, 'key':'value'} into 'class key="value"' """

    return ' '.join(["{}={}".format(key, dumps(metadata[key]))
                     if metadata[key] is not None else key for key in metadata])


def parse_md_code_options(options):
    """Parse 'python class key="value"' into [('python', None), ('class', None), ('key', 'value')]"""

    metadata = []
    while options:
        name_and_value = re.split(r'[\s=]+', options, maxsplit=1)
        name = name_and_value[0]

        # Equal sign in between name and what's next?
        if len(name_and_value) == 2:
            sep = options[len(name):-len(name_and_value[1])]
            has_value = sep.find('=') >= 0
            options = name_and_value[1]
        else:
            has_value = False
            options = ''

        if not has_value:
            metadata.append((name, None))
            continue

        try:
            value = loads(options)
            options = ''
        except JSONDecodeError as err:
            try:
                split = err.colno - 1
            except AttributeError:
                # str(err) is like: "ValueError: Extra data: line 1 column 7 - line 1 column 50 (char 6 - 49)"
                match = re.match(r'.*char ([0-9]*)', str(err))
                split = int(match.groups()[0])

            value = loads(options[:split])
            options = options[split:]

        metadata.append((name, value))

    return metadata


def md_options_to_metadata(options):
    """Parse markdown options and return language and metadata"""
    metadata = parse_md_code_options(options)

    if metadata:
        language = metadata[0][0]
        for lang in _JUPYTER_LANGUAGES + ['julia', 'scheme', 'c++']:
            if language.lower() == lang.lower():
                return lang, dict(metadata[1:])

    return None, dict(metadata)


def try_eval_metadata(metadata, name):
    """Evaluate given metadata to a python object, if possible"""
    value = metadata[name]
    if not isinstance(value, (str, unicode)):
        return
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        if name in ['active', 'magic_args', 'language']:
            metadata[name] = value[1:-1]
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
        options = loads('{' + options + '}' if add_brackets else options)
        return options
    except ValueError:
        return {}


def metadata_to_json_options(metadata):
    """Represent metadata as json text"""
    for key in _JUPYTEXT_CELL_METADATA:
        metadata.pop(key, None)

    return dumps(metadata)


def is_active(ext, metadata):
    """Is the cell active for the given file extension?"""
    if metadata.get('run_control', {}).get('frozen') is True:
        return False
    for tag in metadata.get('tags', []):
        if tag.startswith('active-'):
            return ext.replace('.', '') in tag.split('-')
    if 'active' not in metadata:
        return True
    return ext.replace('.', '') in re.split('\\.|,', metadata['active'])


def double_percent_options_to_metadata(options):
    """Parse double percent options"""
    matches = _PERCENT_CELL.findall('# %%' + options)

    # Fail safe when regexp matching fails #116
    # (occurs e.g. if square brackets are found in the title)
    if not matches:
        return {'title': options.strip()}

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
    metadata = metadata_to_json_options(metadata)
    if metadata != '{}':
        options.append(metadata)
    return ' '.join(options)
