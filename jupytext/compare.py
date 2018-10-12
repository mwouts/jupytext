"""Compare two Jupyter notebooks"""

from testfixtures import compare
from .cell_metadata import _IGNORE_METADATA
from .jupytext import reads, writes
from .combine import combine_inputs_with_outputs


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


def compare_notebooks(notebook_expected,
                      notebook_actual,
                      allow_split_markdown=False,
                      test_outputs=False):
    """Compare the two notebooks, and raise with a meaningful message
    that explains one difference, if any"""

    # Compare cells type and content
    test_cell_iter = iter(notebook_actual.cells)
    for ref_cell in notebook_expected.cells:
        try:
            test_cell = next(test_cell_iter)
        except StopIteration:
            compare(filtered_cell(ref_cell, preserve_outputs=test_outputs), None)

        if allow_split_markdown and ref_cell.cell_type == 'markdown':
            ref_lines = [line for line in ref_cell.source.splitlines()
                         if line != '']
            test_lines = []

            while True:
                compare(ref_cell.cell_type, test_cell.cell_type)
                compare(ref_cell.metadata, test_cell.metadata)

                test_lines.extend([line for line in test_cell.source.splitlines() if line != ''])

                if len(test_lines) >= len(ref_lines):
                    break

                try:
                    test_cell = next(test_cell_iter)
                except StopIteration:
                    break

            compare(ref_lines, test_lines)
            continue

        ref_cell = filtered_cell(ref_cell, preserve_outputs=test_outputs)
        test_cell = filtered_cell(test_cell, preserve_outputs=test_outputs)

        compare(ref_cell, test_cell)

    # Compare notebook metadata
    compare(filtered_notebook_metadata(notebook_expected),
            filtered_notebook_metadata(notebook_actual))


def test_round_trip_conversion(notebook, ext, format_name, test_outputs):
    """Test round trip conversion for a Jupyter notebook"""
    text = writes(notebook, ext=ext, format_name=format_name)
    round_trip = reads(text, ext=ext, format_name=format_name)

    compare_notebooks(notebook,
                      round_trip,
                      allow_split_markdown=(ext in ['.Rmd', '.md']),
                      test_outputs=False)

    if test_outputs:
        combine_inputs_with_outputs(round_trip, notebook)
        compare_notebooks(notebook,
                          round_trip,
                          allow_split_markdown=(ext in ['.Rmd', '.md']),
                          test_outputs=True)
