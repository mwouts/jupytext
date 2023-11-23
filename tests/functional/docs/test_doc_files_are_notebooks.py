from pathlib import Path

import pytest

from jupytext import read


def documentation_files():
    for path in (Path(__file__).parent / "../../../docs").iterdir():
        if path.suffix == ".md":
            yield path


@pytest.mark.parametrize(
    "doc_file",
    documentation_files(),
    ids=[doc_file.stem for doc_file in documentation_files()],
)
def test_doc_files_are_notebooks(doc_file):
    nb = read(doc_file)

    # count how many cell types
    counts = {"markdown": 0, "raw": 0, "code": 0}
    for cell in nb.cells:
        counts[cell.cell_type] += 1

    assert counts["raw"] <= 1
