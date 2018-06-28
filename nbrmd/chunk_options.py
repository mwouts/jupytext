"""
Convert between R markdown chunk options and jupyter cell metadata.

metadata.hide_input and metadata.hide_output are documented here:
http://jupyter-contrib-nbextensions.readthedocs.io/en/latest/nbextensions/runtools/readme.html

TODO: Update this if a standard gets defined at
https://github.com/jupyter/notebook/issues/3700
"""

import ast

_boolean_options_dictionary = [('hide_input', 'echo', True),
                               ('hide_output', 'include', True)]
_ignore_metadata = ['collapsed', 'autoscroll', 'deletable',
                    'format', 'trusted']


def _r_logical_values(bool):
    return 'TRUE' if bool else 'FALSE'


class RLogicalValueError(Exception):
    pass


class RMarkdownOptionParsingError(Exception):
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
            options += ' {}={},'.format(
                ro, _r_logical_values(metadata[jo] != rev))
            del metadata[jo]
    for co_name in metadata:
        co_value = metadata[co_name]
        co_name = co_name.strip()
        if co_name in _ignore_metadata:
            continue
        elif isinstance(co_value, bool):
            options += ' {}={},'.format(
                co_name, 'TRUE' if co_value else 'FALSE')
        elif isinstance(co_value, list):
            options += ' {}={},'.format(
                co_name, 'c({})'.format(
                    ', '.join(['"{}"'.format(str(v)) for v in co_value])))
        else:
            options += ' {}={},'.format(co_name, str(co_value))
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


class ParsingContext():
    parenthesis_count = 0
    curly_bracket_count = 0
    square_bracket_count = 0
    in_single_quote = False
    in_double_quote = False

    def __init__(self, line):
        self.line = line

    def in_global_expression(self):
        return (self.parenthesis_count == 0 and self.curly_bracket_count == 0
                and self.square_bracket_count == 0
                and not self.in_single_quote and not self.in_double_quote)

    def count_special_chars(self, char, prev_char):
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
    c = ParsingContext(line)

    result = []
    prev_char = ''

    name = ''
    value = ''

    for char in ',' + line + ',':
        if c.in_global_expression():
            if char == ',':
                if name is not '' or value is not '':
                    if len(result) and name is '':
                        raise RMarkdownOptionParsingError(
                            'Option line "{}" has no name for '
                            'option value {}' .format(line, value))
                    result.append((name.strip(), value.strip()))
                    name = ''
                    value = ''
            elif char == '=':
                if name is '':
                    name = value
                    value = ''
                else:
                    value += char
            else:
                c.count_special_chars(char, prev_char)
                value += char
        else:
            c.count_special_chars(char, prev_char)
            value += char
        prev_char = char

    if not c.in_global_expression():
        raise RMarkdownOptionParsingError(
            'Option line "{}" is not properly terminated'.format(line))

    return result


def to_metadata(options):
    options = options.split(' ', 1)
    if len(options) == 1:
        language = options[0]
        chunk_options = []
    else:
        language, others = options
        chunk_options = parse_rmd_options(others)

    language = 'R' if language == 'r' else language
    metadata = {}
    for i, opt in enumerate(chunk_options):
        name, value = opt
        if i == 0 and name is '':
            metadata['name'] = value
            continue
        else:
            if update_metadata_using_dictionary(name, value, metadata):
                continue
            try:
                metadata[name] = _py_logical_values(value)
                continue
            except RLogicalValueError:
                metadata[name] = value

    for m in metadata:
        value = metadata[m]
        if not isinstance(value, str):
            continue
        if value.startswith('"') or value.startswith("'"):
            continue
        if value.startswith('c(') and value.endswith(')'):
            value = '[' + value[2:-1] + ']'
        elif value.startswith('list(') and value.endswith(')'):
            value = '[' + value[5:-1] + ']'
        try:
            metadata[m] = ast.literal_eval(value)
        except (SyntaxError, ValueError):
            continue

    return language, metadata
