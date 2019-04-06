"""Compare two Jupyter notebooks"""

import re
from copy import copy
from testfixtures import compare
from .cell_metadata import _IGNORE_CELL_METADATA
from .header import _DEFAULT_NOTEBOOK_METADATA
from .metadata_filter import filter_metadata
from .jupytext import reads, writes
from .combine import combine_inputs_with_outputs
from .formats import long_form_one_format

_BLANK_LINE = re.compile(r'^\s*$')


def filtered_cell(cell, preserve_outputs, cell_metadata_filter):
    """Cell type, metadata and source from given cell"""
    metadata = copy(cell.metadata)
    filter_metadata(metadata, cell_metadata_filter, _IGNORE_CELL_METADATA)

    filtered = {'cell_type': cell.cell_type,
                'source': cell.source,
                'metadata': metadata}

    if preserve_outputs:
        for key in ['execution_count', 'outputs']:
            if key in cell:
                filtered[key] = cell[key]

    return filtered


def filtered_notebook_metadata(notebook):
    """Notebook metadata, filtered for metadata added by Jupytext itself"""
    metadata = copy(notebook.metadata)
    metadata = filter_metadata(metadata,
                               notebook.metadata.get('jupytext', {}).get('notebook_metadata_filter'),
                               _DEFAULT_NOTEBOOK_METADATA)
    if 'jupytext' in metadata:
        del metadata['jupytext']
    return metadata


class NotebookDifference(Exception):
    """Report notebook differences"""


def same_content(ref_source, test_source, allow_removed_final_blank_line):
    """Is the content of two cells the same, except for an optional final blank line?"""
    if ref_source == test_source:
        return True

    if not allow_removed_final_blank_line:
        return False

    # Is ref identical to test, plus one blank line?
    ref_source = ref_source.splitlines()
    test_source = test_source.splitlines()

    if not ref_source:
        return False

    if ref_source[:-1] != test_source:
        return False

    return _BLANK_LINE.match(ref_source[-1])


def compare_notebooks(notebook_expected,
                      notebook_actual,
                      fmt=None,
                      allow_expected_differences=True,
                      raise_on_first_difference=True,
                      compare_outputs=False):
    """Compare the two notebooks, and raise with a meaningful message
    that explains the differences, if any"""
    fmt = long_form_one_format(fmt)
    format_name = fmt.get('format_name')

    # Expected differences
    allow_filtered_cell_metadata = allow_expected_differences
    allow_missing_code_cell_metadata = allow_expected_differences and format_name == 'sphinx'
    allow_missing_markdown_cell_metadata = allow_expected_differences and format_name in ['sphinx', 'spin']
    allow_removed_final_blank_line = allow_expected_differences
    replace_tabs_with_spaces = format_name == 'pandoc'

    cell_metadata_filter = notebook_actual.get('jupytext', {}).get('cell_metadata_filter')

    if format_name == 'sphinx' and notebook_actual.cells and notebook_actual.cells[0].source == '%matplotlib inline':
        notebook_actual.cells = notebook_actual.cells[1:]

    # Compare cells type and content
    test_cell_iter = iter(notebook_actual.cells)
    modified_cells = set()
    modified_cell_metadata = set()
    for i, ref_cell in enumerate(notebook_expected.cells, 1):
        if replace_tabs_with_spaces and '\t' in ref_cell.source:
            ref_cell = copy(ref_cell)
            ref_cell.source = ref_cell.source.replace('\t', '    ')
        try:
            test_cell = next(test_cell_iter)
        except StopIteration:
            if raise_on_first_difference:
                raise NotebookDifference('No cell corresponding to {} cell #{}:\n{}'
                                         .format(ref_cell.cell_type, i, ref_cell.source))
            modified_cells.update(range(i, len(notebook_expected.cells) + 1))
            break

        ref_lines = [line for line in ref_cell.source.splitlines() if not _BLANK_LINE.match(line)]
        test_lines = []

        # 1. test cell type
        if ref_cell.cell_type != test_cell.cell_type:
            if raise_on_first_difference:
                raise NotebookDifference("Unexpected cell type '{}' for {} cell #{}:\n{}"
                                         .format(test_cell.cell_type, ref_cell.cell_type, i, ref_cell.source))
            modified_cells.add(i)

        # 2. test cell metadata
        if (ref_cell.cell_type == 'code' and not allow_missing_code_cell_metadata) or \
                (ref_cell.cell_type != 'code' and not allow_missing_markdown_cell_metadata):

            if allow_filtered_cell_metadata:
                ref_cell.metadata = {key: ref_cell.metadata[key] for key in ref_cell.metadata
                                     if key not in _IGNORE_CELL_METADATA}
                test_cell.metadata = {key: test_cell.metadata[key] for key in test_cell.metadata
                                      if key not in _IGNORE_CELL_METADATA}

            if ref_cell.metadata != test_cell.metadata:
                if raise_on_first_difference:
                    try:
                        compare(ref_cell.metadata, test_cell.metadata)
                    except AssertionError as error:
                        raise NotebookDifference("Metadata differ on {} cell #{}: {}\nCell content:\n{}"
                                                 .format(test_cell.cell_type, i, str(error), ref_cell.source))
                else:
                    modified_cell_metadata.update(set(test_cell.metadata).difference(ref_cell.metadata))
                    modified_cell_metadata.update(set(ref_cell.metadata).difference(test_cell.metadata))
                    for key in set(ref_cell.metadata).intersection(test_cell.metadata):
                        if ref_cell.metadata[key] != test_cell.metadata[key]:
                            modified_cell_metadata.add(key)

        test_lines.extend([line for line in test_cell.source.splitlines() if not _BLANK_LINE.match(line)])

        # 3. test cell content
        if ref_lines != test_lines:
            if raise_on_first_difference:
                try:
                    compare('\n'.join(ref_lines), '\n'.join(test_lines))
                except AssertionError as error:
                    raise NotebookDifference("Cell content differ on {} cell #{}: {}"
                                             .format(test_cell.cell_type, i, str(error)))
            else:
                modified_cells.add(i)

        # 3. bis test entire cell content
        if not same_content(ref_cell.source, test_cell.source, allow_removed_final_blank_line):
            try:
                compare(ref_cell.source, test_cell.source)
            except AssertionError as error:
                if raise_on_first_difference:
                    raise NotebookDifference("Cell content differ on {} cell #{}: {}"
                                             .format(test_cell.cell_type, i, str(error)))
                modified_cells.add(i)

        if not compare_outputs:
            continue

        if ref_cell.cell_type != 'code':
            continue

        ref_cell = filtered_cell(ref_cell,
                                 preserve_outputs=compare_outputs,
                                 cell_metadata_filter=cell_metadata_filter)
        test_cell = filtered_cell(test_cell,
                                  preserve_outputs=compare_outputs,
                                  cell_metadata_filter=cell_metadata_filter)

        try:
            compare(ref_cell, test_cell)
        except AssertionError as error:
            if raise_on_first_difference:
                raise NotebookDifference("Cell outputs differ on {} cell #{}: {}"
                                         .format(test_cell['cell_type'], i, str(error)))
            modified_cells.add(i)

    # More cells in the actual notebook?
    remaining_cell_count = 0
    while True:
        try:
            test_cell = next(test_cell_iter)
            if raise_on_first_difference:
                raise NotebookDifference('Additional {} cell: {}'.format(test_cell.cell_type, test_cell.source))
            remaining_cell_count += 1
        except StopIteration:
            break

    if remaining_cell_count and not raise_on_first_difference:
        modified_cells.update(
            range(len(notebook_expected.cells) + 1, len(notebook_expected.cells) + 1 + remaining_cell_count))

    # Compare notebook metadata
    modified_metadata = False
    try:
        compare(filtered_notebook_metadata(notebook_expected),
                filtered_notebook_metadata(notebook_actual))
    except AssertionError as error:
        if raise_on_first_difference:
            raise NotebookDifference("Notebook metadata differ: {}".format(str(error)))
        modified_metadata = True

    error = []
    if modified_cells:
        error.append('Cells {} differ ({}/{})'.format(','.join([str(i) for i in modified_cells]),
                                                      len(modified_cells), len(notebook_expected.cells)))
    if modified_cell_metadata:
        error.append("Cell metadata '{}' differ".format("', '".join([str(i) for i in modified_cell_metadata])))
    if modified_metadata:
        error.append('Notebook metadata differ')

    if error:
        raise NotebookDifference(' | '.join(error))


def test_round_trip_conversion(notebook, fmt, update, allow_expected_differences=True, stop_on_first_error=True):
    """Test round trip conversion for a Jupyter notebook"""
    text = writes(notebook, fmt)
    round_trip = reads(text, fmt)

    if update:
        combine_inputs_with_outputs(round_trip, notebook, fmt)

    compare_notebooks(notebook, round_trip, fmt, allow_expected_differences,
                      raise_on_first_difference=stop_on_first_error)
