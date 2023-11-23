import pytest

from jupytext import read, reads, writes
from jupytext.formats import JupytextFormatError, auto_ext_from_metadata


def test_auto_in_fmt(ipynb_py_R_file):
    nb = read(ipynb_py_R_file)
    auto_ext = auto_ext_from_metadata(nb.metadata)
    fmt = auto_ext[1:] + ":percent"
    text = writes(nb, "auto:percent")

    assert "auto" not in text

    nb2 = reads(text, fmt)
    assert nb2.metadata["jupytext"]["text_representation"]["extension"]
    assert nb2.metadata["jupytext"]["text_representation"]["format_name"] == "percent"

    del nb.metadata["language_info"]
    del nb.metadata["kernelspec"]
    with pytest.raises(JupytextFormatError):
        writes(nb, "auto:percent")


def test_auto_from_kernelspecs_works(ipynb_file):
    nb = read(ipynb_file)
    language_info = nb.metadata.pop("language_info")
    expected_ext = language_info.get("file_extension")
    if not expected_ext:
        pytest.skip("No file_extension in language_info")
    if expected_ext == ".r":
        expected_ext = ".R"
    elif expected_ext == ".fs":
        expected_ext = ".fsx"
    auto_ext = auto_ext_from_metadata(nb.metadata)
    if auto_ext == ".sage":
        pytest.skip(
            "Sage notebooks have Python in their language_info metadata, see #727"
        )
    assert auto_ext == expected_ext


def test_auto_in_formats(ipynb_py_R_jl_file):
    if any(pattern in ipynb_py_R_jl_file for pattern in ["plotly", "julia"]):
        pytest.skip()
    nb = read(ipynb_py_R_jl_file)
    nb.metadata["jupytext"] = {"formats": "ipynb,auto:percent"}
    fmt = auto_ext_from_metadata(nb.metadata)[1:] + ":percent"
    expected_formats = "ipynb," + fmt

    text = writes(nb, "ipynb")
    assert "auto" not in text
    nb2 = reads(text, "ipynb")
    assert nb2.metadata["jupytext"]["formats"] == expected_formats

    text = writes(nb, "auto:percent")
    assert "auto" not in text
    nb2 = reads(text, fmt)
    assert nb2.metadata["jupytext"]["formats"] == expected_formats

    del nb.metadata["language_info"]
    del nb.metadata["kernelspec"]
    with pytest.raises(JupytextFormatError):
        writes(nb, "ipynb")
    with pytest.raises(JupytextFormatError):
        writes(nb, "auto:percent")
