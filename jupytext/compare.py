"""Compare two Jupyter notebooks"""

import re
from testfixtures import compare
from .cell_metadata import _IGNORE_METADATA
from .jupytext import reads, writes
from .combine import combine_inputs_with_outputs

_BLANK_LINE = re.compile(r'^\s*$')


def filtered_cell(cell, preserve_outputs):
    """Cell type, metadata and source from given cell"""
    filtered = {'cell_type': cell.cell_type,
                'source': cell.source,
                'metadata': {key: cell.metadata[key] for key in cell.metadata if key not in _IGNORE_METADATA}}

    if preserve_outputs:
        for key in ['execution_count', 'outputs']:
            if key in cell:
                filtered[key] = cell[key]

    return filtered


def filtered_notebook_metadata(notebook):
    """Notebook metadata, filtered for metadata added by Jupytext itself"""
    return {key: notebook.metadata[key] for key in notebook.metadata if key != 'jupytext'}


class NotebookDifference(Exception):
    """Report notebook differences"""
    pass


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
                      ext=None,
                      format_name=None,
                      allow_expected_differences=True,
                      raise_on_first_difference=True,
                      compare_outputs=False):
    """Compare the two notebooks, and raise with a meaningful message
    that explains the differences, if any"""

    # Expected differences
    allow_filtered_cell_metadata = allow_expected_differences
    allow_splitted_markdown_cells = allow_expected_differences and ext in ['.md', '.Rmd']
    allow_missing_code_cell_metadata = allow_expected_differences and (ext in ['.md'] or format_name == 'sphinx')
    allow_missing_markdown_cell_metadata = allow_expected_differences and (ext in ['.md', '.Rmd']
                                                                           or format_name in ['sphinx', 'spin'])
    allow_removed_final_blank_line = allow_expected_differences

    # Compare cells type and content
    test_cell_iter = iter(notebook_actual.cells)
    modified_cells = set()
    modified_cell_metadata = set()
    for i, ref_cell in enumerate(notebook_expected.cells, 1):
        try:
            test_cell = next(test_cell_iter)
        except StopIteration:
            if raise_on_first_difference:
                raise NotebookDifference('No cell corresponding to {} cell #{}:\n{}'
                                         .format(ref_cell.cell_type, i, ref_cell.source))
            else:
                modified_cells.update(range(i, len(notebook_expected.cells) + 1))
            break

        ref_lines = [line for line in ref_cell.source.splitlines() if not _BLANK_LINE.match(line)]
        test_lines = []

        while True:
            # 1. test cell type
            if ref_cell.cell_type != test_cell.cell_type:
                if raise_on_first_difference:
                    raise NotebookDifference("Unexpected cell type '{}' for {} cell #{}:\n{}"
                                             .format(test_cell.cell_type, ref_cell.cell_type, i, ref_cell.source))
                else:
                    modified_cells.add(i)

            # 2. test cell metadata
            if (ref_cell.cell_type == 'code' and not allow_missing_code_cell_metadata) or \
                    (ref_cell.cell_type != 'code' and not allow_missing_markdown_cell_metadata):

                if allow_filtered_cell_metadata:
                    ref_cell.metadata = {key: ref_cell.metadata[key] for key in ref_cell.metadata
                                         if key not in _IGNORE_METADATA}
                    test_cell.metadata = {key: test_cell.metadata[key] for key in test_cell.metadata
                                          if key not in _IGNORE_METADATA}

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

            if ref_cell.cell_type != 'markdown':
                break

            if not allow_splitted_markdown_cells:
                break

            if len(test_lines) >= len(ref_lines):
                break

            try:
                test_cell = next(test_cell_iter)
            except StopIteration:
                break

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
        if ref_cell.cell_type != 'markdown' or not allow_splitted_markdown_cells:
            if not same_content(ref_cell.source, test_cell.source, allow_removed_final_blank_line):
                try:
                    compare(ref_cell.source, test_cell.source)
                except AssertionError as error:
                    if raise_on_first_difference:
                        raise NotebookDifference("Cell content differ on {} cell #{}: {}"
                                                 .format(test_cell.cell_type, i, str(error)))
                    else:
                        modified_cells.add(i)

        if not compare_outputs:
            continue

        if ref_cell.cell_type != 'code':
            continue

        ref_cell = filtered_cell(ref_cell, preserve_outputs=compare_outputs)
        test_cell = filtered_cell(test_cell, preserve_outputs=compare_outputs)

        try:
            compare(ref_cell, test_cell)
        except AssertionError as error:
            if raise_on_first_difference:
                raise NotebookDifference("Cell outputs differ on {} cell #{}: {}"
                                         .format(test_cell['cell_type'], i, str(error)))
            else:
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
        else:
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


def test_round_trip_conversion(notebook, ext, format_name, update,
                               allow_expected_differences=True,
                               stop_on_first_error=True):
    """Test round trip conversion for a Jupyter notebook"""
    text = writes(notebook, ext=ext, format_name=format_name)
    round_trip = reads(text, ext=ext, format_name=format_name)

    if update:
        combine_inputs_with_outputs(round_trip, notebook)

    compare_notebooks(notebook, round_trip, ext, format_name, allow_expected_differences,
                      raise_on_first_difference=stop_on_first_error)
