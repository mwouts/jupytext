from pathlib import Path
import re
import pytest
import sys


def replace_issue_number_with_links(text):
    return re.sub(
        r"([^\[])#([0-9]+)",
        r"\1[#\2](https://github.com/mwouts/jupytext/issues/\2)",
        text,
    )


@pytest.mark.parametrize(
    "input,output",
    [
        (
            "Issue #535",
            "Issue [#535](https://github.com/mwouts/jupytext/issues/535)",
        ),
        (
            "Multiline\ntext (#123)",
            "Multiline\ntext ([#123](https://github.com/mwouts/jupytext/issues/123))",
        ),
    ],
)
def test_replace_issue_numbers_with_links(input, output):
    assert replace_issue_number_with_links(input) == output


@pytest.mark.skipif(
    sys.version_info < (3, 5), reason="'PosixPath' object has no attribute 'read_text'"
)
def test_update_changelog():
    changelog_file = Path(__file__).parent.parent / "docs" / "CHANGELOG.md"
    cur_text = changelog_file.read_text()
    new_text = replace_issue_number_with_links(cur_text)
    if cur_text != new_text:
        changelog_file.write_text(new_text)  # pragma: no cover
