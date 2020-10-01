# coding: utf-8

import os
import re
import time
import pytest
import itertools
import logging
import shutil
from nbformat.v4.nbbase import new_notebook, new_markdown_cell, new_code_cell
from tornado.web import HTTPError
from jupytext.compare import compare
import jupytext
from jupytext.cli import jupytext as jupytext_cli
from jupytext.jupytext import writes, write, read
from jupytext.compare import compare_notebooks
from jupytext.header import header_to_metadata_and_cell
from jupytext.formats import read_format_from_metadata, auto_ext_from_metadata
from jupytext.kernels import kernelspec_from_language
from .utils import (
    list_notebooks,
    requires_sphinx_gallery,
    requires_pandoc,
    skip_if_dict_is_not_ordered,
    notebook_model,
)


def test_create_contentsmanager():
    jupytext.TextFileContentsManager()


def test_rename(tmpdir):
    org_file = str(tmpdir.join("notebook.ipynb"))
    new_file = str(tmpdir.join("new.ipynb"))
    jupytext.write(new_notebook(), org_file)

    cm = jupytext.TextFileContentsManager()
    cm.root_dir = str(tmpdir)
    cm.rename_file("notebook.ipynb", "new.ipynb")

    assert os.path.isfile(new_file)
    assert not os.path.isfile(org_file)


def test_rename_inconsistent_path(tmpdir):
    org_file = str(tmpdir.join("notebook_suffix.ipynb"))
    new_file = str(tmpdir.join("new.ipynb"))
    jupytext.write(
        new_notebook(metadata={"jupytext": {"formats": "_suffix.ipynb"}}), org_file
    )

    cm = jupytext.TextFileContentsManager()
    cm.root_dir = str(tmpdir)
    # Read notebook, and learn about its format
    cm.get("notebook_suffix.ipynb")
    with pytest.raises(HTTPError):
        cm.rename_file("notebook_suffix.ipynb", "new.ipynb")

    assert not os.path.isfile(new_file)
    assert os.path.isfile(org_file)


def test_pair_unpair_notebook(tmpdir):
    tmp_ipynb = "notebook.ipynb"
    tmp_md = "notebook.md"

    nb = new_notebook(
        metadata={
            "kernelspec": {
                "display_name": "Python3",
                "language": "python",
                "name": "python3",
            }
        },
        cells=[
            new_code_cell(
                "1 + 1",
                outputs=[
                    {
                        "data": {"text/plain": ["2"]},
                        "execution_count": 1,
                        "metadata": {},
                        "output_type": "execute_result",
                    }
                ],
            )
        ],
    )

    cm = jupytext.TextFileContentsManager()
    cm.root_dir = str(tmpdir)

    # save notebook
    cm.save(model=notebook_model(nb), path=tmp_ipynb)
    assert not os.path.isfile(str(tmpdir.join(tmp_md)))

    # pair notebook
    nb["metadata"]["jupytext"] = {"formats": "ipynb,md"}
    cm.save(model=notebook_model(nb), path=tmp_ipynb)
    assert os.path.isfile(str(tmpdir.join(tmp_md)))

    # reload and get outputs
    nb2 = cm.get(tmp_md)["content"]
    compare_notebooks(nb, nb2)

    # unpair and save as md
    del nb["metadata"]["jupytext"]
    cm.save(model=notebook_model(nb), path=tmp_md)
    nb2 = cm.get(tmp_md)["content"]

    # we get no outputs here
    compare_notebooks(nb, nb2, compare_outputs=False)
    assert len(nb2.cells[0]["outputs"]) == 0


@skip_if_dict_is_not_ordered
@pytest.mark.parametrize("nb_file", list_notebooks("ipynb", skip="66"))
def test_load_save_rename(nb_file, tmpdir):
    tmp_ipynb = "notebook.ipynb"
    tmp_rmd = "notebook.Rmd"

    cm = jupytext.TextFileContentsManager()
    cm.default_jupytext_formats = "ipynb,Rmd"
    cm.root_dir = str(tmpdir)

    # open ipynb, save Rmd, reopen
    nb = jupytext.read(nb_file)
    cm.save(model=notebook_model(nb), path=tmp_rmd)
    nb_rmd = cm.get(tmp_rmd)
    compare_notebooks(nb_rmd["content"], nb, "Rmd")

    # save ipynb
    cm.save(model=notebook_model(nb), path=tmp_ipynb)

    # rename ipynb
    cm.rename(tmp_ipynb, "new.ipynb")
    assert not os.path.isfile(str(tmpdir.join(tmp_ipynb)))
    assert not os.path.isfile(str(tmpdir.join(tmp_rmd)))

    assert os.path.isfile(str(tmpdir.join("new.ipynb")))
    assert os.path.isfile(str(tmpdir.join("new.Rmd")))

    # delete one file, test that we can still read and rename it
    cm.delete("new.Rmd")
    assert not os.path.isfile(str(tmpdir.join("new.Rmd")))
    model = cm.get("new.ipynb", content=False)
    assert "last_modified" in model
    cm.save(model=notebook_model(nb), path="new.ipynb")
    assert os.path.isfile(str(tmpdir.join("new.Rmd")))

    cm.delete("new.Rmd")
    cm.rename("new.ipynb", tmp_ipynb)

    assert os.path.isfile(str(tmpdir.join(tmp_ipynb)))
    assert not os.path.isfile(str(tmpdir.join(tmp_rmd)))
    assert not os.path.isfile(str(tmpdir.join("new.ipynb")))
    assert not os.path.isfile(str(tmpdir.join("new.Rmd")))


@skip_if_dict_is_not_ordered
@pytest.mark.parametrize("nb_file", list_notebooks("ipynb", skip="magic"))
def test_save_load_paired_md_notebook(nb_file, tmpdir):
    tmp_ipynb = "notebook.ipynb"
    tmp_md = "notebook.md"

    cm = jupytext.TextFileContentsManager()
    cm.root_dir = str(tmpdir)

    # open ipynb, save with cm, reopen
    nb = jupytext.read(nb_file)
    nb.metadata["jupytext"] = {"formats": "ipynb,md"}

    cm.save(model=notebook_model(nb), path=tmp_ipynb)
    nb_md = cm.get(tmp_md)

    compare_notebooks(nb_md["content"], nb, "md")
    assert nb_md["content"].metadata["jupytext"]["formats"] == "ipynb,md"


@requires_pandoc
@skip_if_dict_is_not_ordered
@pytest.mark.parametrize(
    "nb_file",
    list_notebooks("ipynb", skip="(functional|Notebook with|flavors|invalid|305)"),
)
def test_save_load_paired_md_pandoc_notebook(nb_file, tmpdir):
    tmp_ipynb = "notebook.ipynb"
    tmp_md = "notebook.md"

    cm = jupytext.TextFileContentsManager()
    cm.root_dir = str(tmpdir)

    # open ipynb, save with cm, reopen
    nb = jupytext.read(nb_file)
    nb.metadata["jupytext"] = {"formats": "ipynb,md:pandoc"}

    cm.save(model=notebook_model(nb), path=tmp_ipynb)
    nb_md = cm.get(tmp_md)

    compare_notebooks(nb_md["content"], nb, "md:pandoc")
    assert nb_md["content"].metadata["jupytext"]["formats"] == "ipynb,md:pandoc"


@skip_if_dict_is_not_ordered
@pytest.mark.parametrize("py_file", list_notebooks("percent"))
def test_pair_plain_script(py_file, tmpdir, caplog):
    tmp_py = "notebook.py"
    tmp_ipynb = "notebook.ipynb"

    cm = jupytext.TextFileContentsManager()
    cm.root_dir = str(tmpdir)

    # open py file, pair, save with cm
    nb = jupytext.read(py_file)
    nb.metadata["jupytext"]["formats"] = "ipynb,py:hydrogen"
    cm.save(model=notebook_model(nb), path=tmp_py)

    assert "'Include Metadata' is off" in caplog.text

    assert os.path.isfile(str(tmpdir.join(tmp_py)))
    assert os.path.isfile(str(tmpdir.join(tmp_ipynb)))

    # Make sure we've not changed the script
    with open(py_file) as fp:
        script = fp.read()

    with open(str(tmpdir.join(tmp_py))) as fp:
        script2 = fp.read()

    compare(script2, script)

    # reopen py file with the cm
    nb2 = cm.get(tmp_py)["content"]
    compare_notebooks(nb2, nb)
    assert nb2.metadata["jupytext"]["formats"] == "ipynb,py:hydrogen"

    # remove the pairing and save
    del nb.metadata["jupytext"]["formats"]
    cm.save(model=notebook_model(nb), path=tmp_py)

    # reopen py file with the cm
    nb2 = cm.get(tmp_py)["content"]
    compare_notebooks(nb2, nb)
    assert "formats" not in nb2.metadata["jupytext"]


@skip_if_dict_is_not_ordered
@pytest.mark.parametrize("nb_file", list_notebooks("ipynb_py"))
def test_load_save_rename_nbpy(nb_file, tmpdir):
    tmp_ipynb = "notebook.ipynb"
    tmp_nbpy = "notebook.nb.py"

    cm = jupytext.TextFileContentsManager()
    cm.default_jupytext_formats = "ipynb,.nb.py"
    cm.root_dir = str(tmpdir)

    # open ipynb, save nb.py, reopen
    nb = jupytext.read(nb_file)
    cm.save(model=notebook_model(nb), path=tmp_nbpy)
    nbpy = cm.get(tmp_nbpy)
    compare_notebooks(nbpy["content"], nb)

    # save ipynb
    cm.save(model=notebook_model(nb), path=tmp_ipynb)

    # rename nbpy
    cm.rename(tmp_nbpy, "new.nb.py")
    assert not os.path.isfile(str(tmpdir.join(tmp_ipynb)))
    assert not os.path.isfile(str(tmpdir.join(tmp_nbpy)))

    assert os.path.isfile(str(tmpdir.join("new.ipynb")))
    assert os.path.isfile(str(tmpdir.join("new.nb.py")))

    # rename to a non-matching pattern
    with pytest.raises(HTTPError):
        cm.rename_file(tmp_nbpy, "suffix_missing.py")


@skip_if_dict_is_not_ordered
@pytest.mark.parametrize("script", list_notebooks("python", skip="light"))
def test_load_save_py_freeze_metadata(script, tmpdir):
    tmp_nbpy = "notebook.py"

    cm = jupytext.TextFileContentsManager()
    cm.root_dir = str(tmpdir)

    # read original file
    with open(script) as fp:
        text_py = fp.read()

    # write to tmp_nbpy
    with open(str(tmpdir.join(tmp_nbpy)), "w") as fp:
        fp.write(text_py)

    # open and save notebook
    nb = cm.get(tmp_nbpy)["content"]
    cm.save(model=notebook_model(nb), path=tmp_nbpy)

    with open(str(tmpdir.join(tmp_nbpy))) as fp:
        text_py2 = fp.read()

    compare(text_py2, text_py)


@skip_if_dict_is_not_ordered
@pytest.mark.parametrize("nb_file", list_notebooks("ipynb_py"))
def test_load_save_rename_notebook_with_dot(nb_file, tmpdir):
    tmp_ipynb = "1.notebook.ipynb"
    tmp_nbpy = "1.notebook.py"

    cm = jupytext.TextFileContentsManager()
    cm.default_jupytext_formats = "ipynb,py"
    cm.root_dir = str(tmpdir)

    # open ipynb, save nb.py, reopen
    nb = jupytext.read(nb_file)
    cm.save(model=notebook_model(nb), path=tmp_nbpy)
    nbpy = cm.get(tmp_nbpy)
    compare_notebooks(nbpy["content"], nb)

    # save ipynb
    cm.save(model=notebook_model(nb), path=tmp_ipynb)

    # rename py
    cm.rename(tmp_nbpy, "2.new_notebook.py")
    assert not os.path.isfile(str(tmpdir.join(tmp_ipynb)))
    assert not os.path.isfile(str(tmpdir.join(tmp_nbpy)))

    assert os.path.isfile(str(tmpdir.join("2.new_notebook.ipynb")))
    assert os.path.isfile(str(tmpdir.join("2.new_notebook.py")))


@skip_if_dict_is_not_ordered
@pytest.mark.parametrize("nb_file", list_notebooks("ipynb_py"))
def test_load_save_rename_nbpy_default_config(nb_file, tmpdir):
    tmp_ipynb = "notebook.ipynb"
    tmp_nbpy = "notebook.nb.py"

    cm = jupytext.TextFileContentsManager()
    cm.default_jupytext_formats = "ipynb,.nb.py"
    cm.root_dir = str(tmpdir)

    # open ipynb, save nb.py, reopen
    nb = jupytext.read(nb_file)

    cm.save(model=notebook_model(nb), path=tmp_nbpy)
    nbpy = cm.get(tmp_nbpy)
    compare_notebooks(nbpy["content"], nb)

    # open ipynb
    nbipynb = cm.get(tmp_ipynb)
    compare_notebooks(nbipynb["content"], nb)

    # save ipynb
    cm.save(model=notebook_model(nb), path=tmp_ipynb)

    # rename notebook.nb.py to new.nb.py
    cm.rename(tmp_nbpy, "new.nb.py")
    assert not os.path.isfile(str(tmpdir.join(tmp_ipynb)))
    assert not os.path.isfile(str(tmpdir.join(tmp_nbpy)))

    assert os.path.isfile(str(tmpdir.join("new.ipynb")))
    assert os.path.isfile(str(tmpdir.join("new.nb.py")))

    # rename new.ipynb to notebook.ipynb
    cm.rename("new.ipynb", tmp_ipynb)
    assert os.path.isfile(str(tmpdir.join(tmp_ipynb)))
    assert os.path.isfile(str(tmpdir.join(tmp_nbpy)))

    assert not os.path.isfile(str(tmpdir.join("new.ipynb")))
    assert not os.path.isfile(str(tmpdir.join("new.nb.py")))


@pytest.mark.parametrize("nb_file", list_notebooks("ipynb_py"))
def test_load_save_rename_non_ascii_path(nb_file, tmpdir):
    tmp_ipynb = u"notebôk.ipynb"
    tmp_nbpy = u"notebôk.nb.py"

    cm = jupytext.TextFileContentsManager()
    cm.default_jupytext_formats = "ipynb,.nb.py"
    tmpdir = u"" + str(tmpdir)
    cm.root_dir = tmpdir

    # open ipynb, save nb.py, reopen
    nb = jupytext.read(nb_file)

    cm.save(model=notebook_model(nb), path=tmp_nbpy)
    nbpy = cm.get(tmp_nbpy)
    compare_notebooks(nbpy["content"], nb)

    # open ipynb
    nbipynb = cm.get(tmp_ipynb)
    compare_notebooks(nbipynb["content"], nb)

    # save ipynb
    cm.save(model=notebook_model(nb), path=tmp_ipynb)

    # rename notebôk.nb.py to nêw.nb.py
    cm.rename(tmp_nbpy, u"nêw.nb.py")
    assert not os.path.isfile(os.path.join(tmpdir, tmp_ipynb))
    assert not os.path.isfile(os.path.join(tmpdir, tmp_nbpy))

    assert os.path.isfile(os.path.join(tmpdir, u"nêw.ipynb"))
    assert os.path.isfile(os.path.join(tmpdir, u"nêw.nb.py"))

    # rename nêw.ipynb to notebôk.ipynb
    cm.rename(u"nêw.ipynb", tmp_ipynb)
    assert os.path.isfile(os.path.join(tmpdir, tmp_ipynb))
    assert os.path.isfile(os.path.join(tmpdir, tmp_nbpy))

    assert not os.path.isfile(os.path.join(tmpdir, u"nêw.ipynb"))
    assert not os.path.isfile(os.path.join(tmpdir, u"nêw.nb.py"))


@pytest.mark.parametrize("nb_file", list_notebooks("ipynb_py")[:1])
def test_outdated_text_notebook(nb_file, tmpdir):
    # 1. write py ipynb
    tmp_ipynb = u"notebook.ipynb"
    tmp_nbpy = u"notebook.py"

    cm = jupytext.TextFileContentsManager()
    cm.default_jupytext_formats = "py,ipynb"
    cm.outdated_text_notebook_margin = 0
    cm.root_dir = str(tmpdir)

    # open ipynb, save py, reopen
    nb = jupytext.read(nb_file)
    cm.save(model=notebook_model(nb), path=tmp_nbpy)
    model_py = cm.get(tmp_nbpy, load_alternative_format=False)
    model_ipynb = cm.get(tmp_ipynb, load_alternative_format=False)

    # 2. check that time of ipynb <= py
    assert model_ipynb["last_modified"] <= model_py["last_modified"]

    # 3. wait some time
    time.sleep(0.5)

    # 4. touch ipynb
    with open(str(tmpdir.join(tmp_ipynb)), "a"):
        os.utime(str(tmpdir.join(tmp_ipynb)), None)

    # 5. test error
    with pytest.raises(HTTPError):
        cm.get(tmp_nbpy)

    # 6. test OK with
    cm.outdated_text_notebook_margin = 1.0
    cm.get(tmp_nbpy)

    # 7. test OK with
    cm.outdated_text_notebook_margin = float("inf")
    cm.get(tmp_nbpy)


@pytest.mark.parametrize("nb_file", list_notebooks("ipynb_py")[:1])
def test_reload_notebook_after_jupytext_cli(nb_file, tmpdir):
    tmp_ipynb = str(tmpdir.join("notebook.ipynb"))
    tmp_nbpy = str(tmpdir.join("notebook.py"))

    cm = jupytext.TextFileContentsManager()
    cm.outdated_text_notebook_margin = 0
    cm.root_dir = str(tmpdir)

    # write the paired notebook
    nb = jupytext.read(nb_file)
    nb.metadata.setdefault("jupytext", {})["formats"] = "py,ipynb"
    cm.save(model=notebook_model(nb), path="notebook.py")

    assert os.path.isfile(tmp_ipynb)
    assert os.path.isfile(tmp_nbpy)

    # run jupytext CLI
    jupytext_cli([tmp_nbpy, "--to", "ipynb", "--update"])

    # test reload
    nb1 = cm.get("notebook.py")["content"]
    nb2 = cm.get("notebook.ipynb")["content"]

    compare_notebooks(nb, nb1)
    compare_notebooks(nb, nb2)


@skip_if_dict_is_not_ordered
@pytest.mark.parametrize("nb_file", list_notebooks("percent"))
def test_load_save_percent_format(nb_file, tmpdir):
    tmp_py = "notebook.py"
    with open(nb_file) as stream:
        text_py = stream.read()
    with open(str(tmpdir.join(tmp_py)), "w") as stream:
        stream.write(text_py)

    cm = jupytext.TextFileContentsManager()
    cm.root_dir = str(tmpdir)

    # open python, save
    nb = cm.get(tmp_py)["content"]
    del nb.metadata["jupytext"]["notebook_metadata_filter"]
    cm.save(model=notebook_model(nb), path=tmp_py)

    # compare the new file with original one
    with open(str(tmpdir.join(tmp_py))) as stream:
        text_py2 = stream.read()

    # do we find 'percent' in the header?
    header = text_py2[: -len(text_py)]
    assert any(["percent" in line for line in header.splitlines()])

    # Remove the YAML header
    text_py2 = text_py2[-len(text_py) :]

    compare(text_py2, text_py)


@skip_if_dict_is_not_ordered
@pytest.mark.parametrize("nb_file", list_notebooks("ipynb_julia"))
def test_save_to_percent_format(nb_file, tmpdir):
    tmp_ipynb = "notebook.ipynb"
    tmp_jl = "notebook.jl"

    cm = jupytext.TextFileContentsManager()
    cm.root_dir = str(tmpdir)
    cm.preferred_jupytext_formats_save = "jl:percent"

    nb = jupytext.read(nb_file)
    nb["metadata"]["jupytext"] = {"formats": "ipynb,jl"}

    # save to ipynb and jl
    cm.save(model=notebook_model(nb), path=tmp_ipynb)

    # read jl file
    with open(str(tmpdir.join(tmp_jl))) as stream:
        text_jl = stream.read()

    # Parse the YAML header
    metadata, _, _, _ = header_to_metadata_and_cell(text_jl.splitlines(), "#")
    assert metadata["jupytext"]["formats"] == "ipynb,jl:percent"


@skip_if_dict_is_not_ordered
@pytest.mark.parametrize("nb_file", list_notebooks("ipynb_py"))
def test_save_using_preferred_and_default_format_170(nb_file, tmpdir):
    nb = read(nb_file)

    # Way 0: preferred_jupytext_formats_save, no prefix + default_jupytext_formats
    tmp_py = str(tmpdir.join("python/notebook.py"))

    cm = jupytext.TextFileContentsManager()
    cm.root_dir = str(tmpdir)
    cm.preferred_jupytext_formats_save = "py:percent"
    cm.default_jupytext_formats = "ipynb,python//py"

    # save to ipynb and py
    cm.save(model=notebook_model(nb), path="notebook.ipynb")

    # read py file
    nb_py = read(tmp_py)
    assert nb_py.metadata["jupytext"]["text_representation"]["format_name"] == "percent"

    # Way 1: preferred_jupytext_formats_save + default_jupytext_formats
    tmp_py = str(tmpdir.join("python/notebook.py"))

    cm = jupytext.TextFileContentsManager()
    cm.root_dir = str(tmpdir)
    cm.preferred_jupytext_formats_save = "python//py:percent"
    cm.default_jupytext_formats = "ipynb,python//py"

    # save to ipynb and py
    cm.save(model=notebook_model(nb), path="notebook.ipynb")

    # read py file
    nb_py = read(tmp_py)
    assert nb_py.metadata["jupytext"]["text_representation"]["format_name"] == "percent"

    # Way 2: default_jupytext_formats
    tmp_py = str(tmpdir.join("python/notebook.py"))

    cm = jupytext.TextFileContentsManager()
    cm.root_dir = str(tmpdir)
    cm.default_jupytext_formats = "ipynb,python//py:percent"

    # save to ipynb and py
    cm.save(model=notebook_model(nb), path="notebook.ipynb")

    # read py file
    nb_py = read(tmp_py)
    assert nb_py.metadata["jupytext"]["text_representation"]["format_name"] == "percent"


@skip_if_dict_is_not_ordered
@pytest.mark.parametrize("nb_file", list_notebooks("ipynb_py"))
def test_open_using_preferred_and_default_format_174(nb_file, tmpdir):
    tmp_ipynb = str(tmpdir.join("notebook.ipynb"))
    tmp_py = str(tmpdir.join("python/notebook.py"))
    tmp_py2 = str(tmpdir.join("other/notebook.py"))
    os.makedirs(str(tmpdir.join("other")))
    shutil.copyfile(nb_file, tmp_ipynb)

    cm = jupytext.TextFileContentsManager()
    cm.root_dir = str(tmpdir)
    cm.default_jupytext_formats = "ipynb,python//py:percent"
    cm.default_notebook_metadata_filter = "all"
    cm.default_cell_metadata_filter = "all"

    # load notebook
    model = cm.get("notebook.ipynb")

    # save to ipynb and py
    cm.save(model=model, path="notebook.ipynb")

    assert os.path.isfile(tmp_py)
    os.remove(tmp_ipynb)

    # read py file
    model2 = cm.get("python/notebook.py")
    compare_notebooks(model2["content"], model["content"])

    # move py file to the another folder
    shutil.move(tmp_py, tmp_py2)
    model2 = cm.get("other/notebook.py")
    compare_notebooks(model2["content"], model["content"])
    cm.save(model=model, path="other/notebook.py")
    assert not os.path.isfile(tmp_ipynb)
    assert not os.path.isfile(str(tmpdir.join("other/notebook.ipynb")))


@skip_if_dict_is_not_ordered
@pytest.mark.parametrize("nb_file", list_notebooks("ipynb_py", skip="many hash"))
def test_kernelspec_are_preserved(nb_file, tmpdir):
    tmp_ipynb = str(tmpdir.join("notebook.ipynb"))
    tmp_py = str(tmpdir.join("notebook.py"))
    shutil.copyfile(nb_file, tmp_ipynb)

    cm = jupytext.TextFileContentsManager()
    cm.root_dir = str(tmpdir)
    cm.default_jupytext_formats = "ipynb,py"
    cm.default_notebook_metadata_filter = "-all"

    # load notebook
    model = cm.get("notebook.ipynb")
    model["content"].metadata["kernelspec"] = {
        "display_name": "Kernel name",
        "language": "python",
        "name": "custom",
    }

    # save to ipynb and py
    cm.save(model=model, path="notebook.ipynb")
    assert os.path.isfile(tmp_py)

    # read ipynb
    model2 = cm.get("notebook.ipynb")
    compare_notebooks(model2["content"], model["content"])


@skip_if_dict_is_not_ordered
@pytest.mark.parametrize("nb_file", list_notebooks("ipynb_py"))
def test_save_to_light_percent_sphinx_format(nb_file, tmpdir):
    tmp_ipynb = "notebook.ipynb"
    tmp_lgt_py = "notebook.lgt.py"
    tmp_pct_py = "notebook.pct.py"
    tmp_spx_py = "notebook.spx.py"

    cm = jupytext.TextFileContentsManager()
    cm.root_dir = str(tmpdir)

    nb = jupytext.read(nb_file)
    nb["metadata"]["jupytext"] = {
        "formats": "ipynb,.pct.py:percent,.lgt.py:light,.spx.py:sphinx"
    }

    # save to ipynb and three python flavors
    cm.save(model=notebook_model(nb), path=tmp_ipynb)

    # read files
    with open(str(tmpdir.join(tmp_pct_py))) as stream:
        assert read_format_from_metadata(stream.read(), ".py") == "percent"

    with open(str(tmpdir.join(tmp_lgt_py))) as stream:
        assert read_format_from_metadata(stream.read(), ".py") == "light"

    with open(str(tmpdir.join(tmp_spx_py))) as stream:
        assert read_format_from_metadata(stream.read(), ".py") == "sphinx"

    model = cm.get(path=tmp_pct_py)
    compare_notebooks(model["content"], nb)

    model = cm.get(path=tmp_lgt_py)
    compare_notebooks(model["content"], nb)

    model = cm.get(path=tmp_spx_py)
    # (notebooks not equal as we insert %matplotlib inline in sphinx)

    model = cm.get(path=tmp_ipynb)
    compare_notebooks(model["content"], nb)


@skip_if_dict_is_not_ordered
@pytest.mark.parametrize("nb_file", list_notebooks("ipynb_py"))
def test_pair_notebook_with_dot(nb_file, tmpdir):
    # Reproduce issue #138
    tmp_py = "file.5.1.py"
    tmp_ipynb = "file.5.1.ipynb"

    cm = jupytext.TextFileContentsManager()
    cm.root_dir = str(tmpdir)

    nb = jupytext.read(nb_file)
    nb["metadata"]["jupytext"] = {"formats": "ipynb,py:percent"}

    # save to ipynb and three python flavors
    cm.save(model=notebook_model(nb), path=tmp_ipynb)

    assert os.path.isfile(str(tmpdir.join(tmp_ipynb)))

    # read files
    with open(str(tmpdir.join(tmp_py))) as stream:
        assert read_format_from_metadata(stream.read(), ".py") == "percent"

    model = cm.get(path=tmp_py)
    assert model["name"] == "file.5.1.py"
    compare_notebooks(model["content"], nb)

    model = cm.get(path=tmp_ipynb)
    assert model["name"] == "file.5.1.ipynb"
    compare_notebooks(model["content"], nb)


@pytest.mark.parametrize("nb_file", list_notebooks("ipynb_py")[:1])
def test_preferred_format_allows_to_read_others_format(nb_file, tmpdir):
    # 1. write py ipynb
    tmp_ipynb = u"notebook.ipynb"
    tmp_nbpy = u"notebook.py"

    cm = jupytext.TextFileContentsManager()
    cm.preferred_jupytext_formats_save = "py:light"
    cm.root_dir = str(tmpdir)

    # load notebook and save it using the cm
    nb = jupytext.read(nb_file)
    nb["metadata"]["jupytext"] = {"formats": "ipynb,py"}
    cm.save(model=notebook_model(nb), path=tmp_ipynb)

    # Saving does not update the metadata, as 'save' makes a copy of the notebook
    # assert nb['metadata']['jupytext']['formats'] == 'ipynb,py:light'

    # Set preferred format for reading
    cm.preferred_jupytext_formats_read = "py:percent"

    # Read notebook
    model = cm.get(tmp_nbpy)

    # Check that format is explicit
    assert model["content"]["metadata"]["jupytext"]["formats"] == "ipynb,py:light"

    # Check contents
    compare_notebooks(model["content"], nb)

    # Change save format and save
    model["content"]["metadata"]["jupytext"]["formats"] == "ipynb,py"
    cm.preferred_jupytext_formats_save = "py:percent"
    cm.save(model=notebook_model(nb), path=tmp_ipynb)

    # Read notebook
    model = cm.get(tmp_nbpy)
    compare_notebooks(model["content"], nb)

    # Check that format is explicit
    assert model["content"]["metadata"]["jupytext"]["formats"] == "ipynb,py:percent"


def test_preferred_formats_read_auto(tmpdir):
    tmp_py = u"notebook.py"
    with open(str(tmpdir.join(tmp_py)), "w") as script:
        script.write(
            """# cell one
1 + 1
"""
        )

    # create contents manager with default load format as percent
    cm = jupytext.TextFileContentsManager()
    cm.preferred_jupytext_formats_read = "auto:percent"
    cm.root_dir = str(tmpdir)

    # load notebook
    model = cm.get(tmp_py)

    # check that script is opened as percent
    assert (
        "percent"
        == model["content"]["metadata"]["jupytext"]["text_representation"][
            "format_name"
        ]
    )


@pytest.mark.parametrize("nb_file", list_notebooks("ipynb"))
def test_save_in_auto_extension_global(nb_file, tmpdir):
    # load notebook
    nb = jupytext.read(nb_file)

    auto_ext = auto_ext_from_metadata(nb.metadata)
    tmp_ipynb = "notebook.ipynb"
    tmp_script = "notebook" + auto_ext

    # create contents manager with default load format as percent
    cm = jupytext.TextFileContentsManager()
    cm.default_jupytext_formats = "ipynb,auto"
    cm.preferred_jupytext_formats_save = "auto:percent"
    cm.root_dir = str(tmpdir)

    # save notebook
    cm.save(model=notebook_model(nb), path=tmp_ipynb)

    # check that text representation exists, and is in percent format
    with open(str(tmpdir.join(tmp_script))) as stream:
        assert read_format_from_metadata(stream.read(), auto_ext) == "percent"

    # reload and compare with original notebook
    model = cm.get(path=tmp_script)

    # saving should not create a format entry #95
    assert "formats" not in model["content"].metadata.get("jupytext", {})

    compare_notebooks(model["content"], nb)


def test_global_auto_pairing_works_with_empty_notebook(tmpdir):
    nb = new_notebook()
    tmp_ipynb = str(tmpdir.join("notebook.ipynb"))
    tmp_py = str(tmpdir.join("notebook.py"))
    tmp_auto = str(tmpdir.join("notebook.auto"))

    # create contents manager with default load format as percent
    cm = jupytext.TextFileContentsManager()
    cm.default_jupytext_formats = "ipynb,auto"
    cm.preferred_jupytext_formats_save = "auto:percent"
    cm.root_dir = str(tmpdir)

    # save notebook
    cm.save(model=notebook_model(nb), path="notebook.ipynb")

    # check that only the ipynb representation exists
    assert os.path.isfile(tmp_ipynb)
    assert not os.path.isfile(tmp_py)
    assert not os.path.isfile(tmp_auto)
    assert "notebook.ipynb" not in cm.paired_notebooks

    model = cm.get(path="notebook.ipynb")
    compare_notebooks(model["content"], nb)

    # add language information to the notebook
    nb.metadata["language_info"] = {
        "codemirror_mode": {"name": "ipython", "version": 3},
        "file_extension": ".py",
        "mimetype": "text/x-python",
        "name": "python",
        "nbconvert_exporter": "python",
        "pygments_lexer": "ipython3",
        "version": "3.7.3",
    }

    # save again
    cm.save(model=notebook_model(nb), path="notebook.ipynb")

    # check that ipynb + py representations exists
    assert os.path.isfile(tmp_ipynb)
    assert os.path.isfile(tmp_py)
    assert not os.path.isfile(tmp_auto)
    assert len(cm.paired_notebooks["notebook.ipynb"]) == 2

    # add a cell in the py file
    with open(tmp_py, "a") as fp:
        fp.write("# %%\n2+2\n")

    nb2 = cm.get(path="notebook.ipynb")["content"]
    assert len(nb2.cells) == 1
    assert nb2.cells[0].source == "2+2"


@pytest.mark.parametrize("nb_file", list_notebooks("ipynb"))
def test_save_in_auto_extension_global_with_format(nb_file, tmpdir):
    # load notebook
    nb = jupytext.read(nb_file)

    auto_ext = auto_ext_from_metadata(nb.metadata)
    tmp_ipynb = "notebook.ipynb"
    tmp_script = "notebook" + auto_ext

    # create contents manager with default load format as percent
    cm = jupytext.TextFileContentsManager()
    cm.default_jupytext_formats = "ipynb,auto:percent"
    cm.root_dir = str(tmpdir)

    # save notebook
    cm.save(model=notebook_model(nb), path=tmp_ipynb)

    # check that text representation exists, and is in percent format
    with open(str(tmpdir.join(tmp_script))) as stream:
        assert read_format_from_metadata(stream.read(), auto_ext) == "percent"

    # reload and compare with original notebook
    model = cm.get(path=tmp_script)

    # saving should not create a format entry #95
    assert "formats" not in model["content"].metadata.get("jupytext", {})

    compare_notebooks(model["content"], nb)


@pytest.mark.parametrize("nb_file", list_notebooks("ipynb"))
def test_save_in_auto_extension_local(nb_file, tmpdir):
    # load notebook
    nb = jupytext.read(nb_file)
    nb.metadata.setdefault("jupytext", {})["formats"] = "ipynb,auto:percent"

    auto_ext = auto_ext_from_metadata(nb.metadata)
    tmp_ipynb = "notebook.ipynb"
    tmp_script = "notebook" + auto_ext

    # create contents manager with default load format as percent
    cm = jupytext.TextFileContentsManager()
    cm.root_dir = str(tmpdir)

    # save notebook
    cm.save(model=notebook_model(nb), path=tmp_ipynb)

    # check that text representation exists, and is in percent format
    with open(str(tmpdir.join(tmp_script))) as stream:
        assert read_format_from_metadata(stream.read(), auto_ext) == "percent"

    # reload and compare with original notebook
    model = cm.get(path=tmp_script)

    compare_notebooks(model["content"], nb)


@pytest.mark.parametrize("nb_file", list_notebooks("ipynb"))
def test_save_in_pct_and_lgt_auto_extensions(nb_file, tmpdir):
    # load notebook
    nb = jupytext.read(nb_file)

    auto_ext = auto_ext_from_metadata(nb.metadata)
    tmp_ipynb = "notebook.ipynb"
    tmp_pct_script = "notebook.pct" + auto_ext
    tmp_lgt_script = "notebook.lgt" + auto_ext

    # create contents manager with default load format as percent
    cm = jupytext.TextFileContentsManager()
    cm.default_jupytext_formats = "ipynb,.pct.auto,.lgt.auto"
    cm.preferred_jupytext_formats_save = ".pct.auto:percent,.lgt.auto:light"
    cm.root_dir = str(tmpdir)

    # save notebook
    cm.save(model=notebook_model(nb), path=tmp_ipynb)

    # check that text representation exists in percent format
    with open(str(tmpdir.join(tmp_pct_script))) as stream:
        assert read_format_from_metadata(stream.read(), auto_ext) == "percent"

    # check that text representation exists in light format
    with open(str(tmpdir.join(tmp_lgt_script))) as stream:
        assert read_format_from_metadata(stream.read(), auto_ext) == "light"


@pytest.mark.parametrize("nb_file", list_notebooks("ipynb", skip="(magic|305)"))
def test_metadata_filter_is_effective(nb_file, tmpdir):
    nb = jupytext.read(nb_file)
    tmp_ipynb = "notebook.ipynb"
    tmp_script = "notebook.py"

    # create contents manager
    cm = jupytext.TextFileContentsManager()
    cm.root_dir = str(tmpdir)

    # save notebook to tmpdir
    cm.save(model=notebook_model(nb), path=tmp_ipynb)

    # set config
    cm.default_jupytext_formats = "ipynb,py"
    cm.default_notebook_metadata_filter = "jupytext,-all"
    cm.default_cell_metadata_filter = "-all"

    # load notebook
    nb = cm.get(tmp_ipynb)["content"]

    assert nb.metadata["jupytext"]["cell_metadata_filter"] == "-all"
    assert nb.metadata["jupytext"]["notebook_metadata_filter"] == "jupytext,-all"

    # save notebook again
    cm.save(model=notebook_model(nb), path=tmp_ipynb)

    # read text version
    nb2 = jupytext.read(str(tmpdir.join(tmp_script)))

    # test no metadata
    assert set(nb2.metadata.keys()) <= {"jupytext", "kernelspec"}
    for cell in nb2.cells:
        assert not cell.metadata

    # read paired notebook
    nb3 = cm.get(tmp_script)["content"]

    compare_notebooks(nb3, nb)


def test_no_metadata_added_to_scripts_139(tmpdir):
    tmp_script = str(tmpdir.join("script.py"))
    text = """import os


print('hello1')



print('hello2')
"""

    with open(tmp_script, "w") as fp:
        fp.write(text)

    # create contents manager
    cm = jupytext.TextFileContentsManager()
    cm.root_dir = str(tmpdir)

    # Andre's config #139
    cm.freeze_metadata = True
    cm.default_notebook_metadata_filter = "-all"
    cm.default_cell_metadata_filter = "-lines_to_next_cell"

    # load notebook
    model = cm.get("script.py")

    # add cell metadata
    for cell in model["content"].cells:
        cell.metadata.update(
            {
                "ExecuteTime": {
                    "start_time": "2019-02-06T11:53:21.208644Z",
                    "end_time": "2019-02-06T11:53:21.213071Z",
                }
            }
        )

    # save notebook
    cm.save(model=model, path="script.py")

    with open(tmp_script) as fp:
        compare(fp.read(), text)


@pytest.mark.parametrize(
    "nb_file,ext", itertools.product(list_notebooks("ipynb_py"), [".py", ".ipynb"])
)
def test_local_format_can_deactivate_pairing(nb_file, ext, tmpdir):
    """This is a test for #157: local format can be used to deactivate the global pairing"""
    nb = jupytext.read(nb_file)
    nb.metadata["jupytext_formats"] = ext[1:]  # py or ipynb

    # create contents manager with default pairing
    cm = jupytext.TextFileContentsManager()
    cm.default_jupytext_formats = "ipynb,py"
    cm.root_dir = str(tmpdir)

    # save notebook
    cm.save(model=notebook_model(nb), path="notebook" + ext)

    # check that only the text representation exists
    assert os.path.isfile(str(tmpdir.join("notebook.py"))) == (ext == ".py")
    assert os.path.isfile(str(tmpdir.join("notebook.ipynb"))) == (ext == ".ipynb")
    nb2 = cm.get("notebook" + ext)["content"]
    compare_notebooks(nb2, nb)

    # resave, check again
    cm.save(model=notebook_model(nb2), path="notebook" + ext)

    assert os.path.isfile(str(tmpdir.join("notebook.py"))) == (ext == ".py")
    assert os.path.isfile(str(tmpdir.join("notebook.ipynb"))) == (ext == ".ipynb")
    nb3 = cm.get("notebook" + ext)["content"]
    compare_notebooks(nb3, nb)


@pytest.mark.parametrize("nb_file", list_notebooks("Rmd"))
def test_global_pairing_allows_to_save_other_file_types(nb_file, tmpdir):
    """This is a another test for #157: local format can be used to deactivate the global pairing"""
    nb = jupytext.read(nb_file)

    # create contents manager with default pairing
    cm = jupytext.TextFileContentsManager()
    cm.default_jupytext_formats = "ipynb,py"
    cm.root_dir = str(tmpdir)

    # save notebook
    cm.save(model=notebook_model(nb), path="notebook.Rmd")

    # check that only the original file is saved
    assert os.path.isfile(str(tmpdir.join("notebook.Rmd")))
    assert not os.path.isfile(str(tmpdir.join("notebook.py")))
    assert not os.path.isfile(str(tmpdir.join("notebook.ipynb")))

    nb2 = cm.get("notebook.Rmd")["content"]
    compare_notebooks(nb2, nb)


@skip_if_dict_is_not_ordered
@pytest.mark.parametrize("nb_file", list_notebooks("R"))
def test_python_kernel_preserves_R_files(nb_file, tmpdir):
    """Opening a R file with a Jupyter server that has no R kernel should not modify the file"""
    tmp_r_file = str(tmpdir.join("script.R"))
    with open(nb_file) as fp:
        script = fp.read()
    with open(tmp_r_file, "w") as fp:
        fp.write(script)

    # create contents manager
    cm = jupytext.TextFileContentsManager()
    cm.root_dir = str(tmpdir)

    # open notebook, set Python kernel and save
    model = cm.get("script.R")
    model["content"].metadata["kernelspec"] = kernelspec_from_language("python")
    cm.save(model=model, path="script.R")

    with open(tmp_r_file) as fp:
        script2 = fp.read()

    compare(script2, script)


def test_pair_notebook_in_another_folder(tmpdir):
    cm = jupytext.TextFileContentsManager()
    cm.root_dir = str(tmpdir)

    os.makedirs(str(tmpdir.join("notebooks")))
    tmp_ipynb = str(tmpdir.join("notebooks/notebook_name.ipynb"))
    tmp_py = str(tmpdir.join("scripts/notebook_name.py"))

    cm.save(
        model=notebook_model(
            new_notebook(
                metadata={"jupytext": {"formats": "notebooks//ipynb,scripts//py"}}
            ),
        ),
        path="notebooks/notebook_name.ipynb",
    )

    assert os.path.isfile(tmp_ipynb)
    assert os.path.isfile(tmp_py)

    cm.get("notebooks/notebook_name.ipynb")
    cm.get("scripts/notebook_name.py")


def test_pair_notebook_in_dotdot_folder(tmpdir):
    cm = jupytext.TextFileContentsManager()
    cm.root_dir = str(tmpdir)

    os.makedirs(str(tmpdir.join("notebooks")))
    tmp_ipynb = str(tmpdir.join("notebooks/notebook_name.ipynb"))
    tmp_py = str(tmpdir.join("scripts/notebook_name.py"))

    cm.save(
        model=notebook_model(
            new_notebook(metadata={"jupytext": {"formats": "ipynb,../scripts//py"}})
        ),
        path="notebooks/notebook_name.ipynb",
    )

    assert os.path.isfile(tmp_ipynb)
    assert os.path.isfile(tmp_py)

    cm.get("notebooks/notebook_name.ipynb")
    cm.get("scripts/notebook_name.py")


@requires_sphinx_gallery
def test_rst2md_option(tmpdir):
    tmp_py = str(tmpdir.join("notebook.py"))

    # Write notebook in sphinx format
    nb = new_notebook(
        cells=[
            new_markdown_cell("A short sphinx notebook"),
            new_markdown_cell(":math:`1+1`"),
        ]
    )
    write(nb, tmp_py, fmt="py:sphinx")

    cm = jupytext.TextFileContentsManager()
    cm.sphinx_convert_rst2md = True
    cm.root_dir = str(tmpdir)

    nb2 = cm.get("notebook.py")["content"]

    # Was rst to md conversion effective?
    assert nb2.cells[2].source == "$1+1$"
    assert nb2.metadata["jupytext"]["rst2md"] is False


def test_split_at_heading_option(tmpdir):
    text = """Markdown text

# Header one

## Header two
"""
    tmp_md = str(tmpdir.join("notebook.md"))
    with open(tmp_md, "w") as fp:
        fp.write(text)

    cm = jupytext.TextFileContentsManager()
    cm.root_dir = str(tmpdir)
    cm.split_at_heading = True

    nb = cm.get("notebook.md")["content"]

    # Was rst to md conversion effective?
    assert nb.cells[0].source == "Markdown text"
    assert nb.cells[1].source == "# Header one"
    assert nb.cells[2].source == "## Header two"

    nb.metadata["jupytext"]["notebook_metadata_filter"] = "-all"
    text2 = writes(nb, "md")
    compare(text2, text)


def test_load_then_change_formats(tmpdir):
    tmp_ipynb = str(tmpdir.join("nb.ipynb"))
    tmp_py = str(tmpdir.join("nb.py"))
    nb = new_notebook(metadata={"jupytext": {"formats": "ipynb,py:light"}})
    write(nb, tmp_ipynb)

    cm = jupytext.TextFileContentsManager()
    cm.root_dir = str(tmpdir)

    model = cm.get("nb.ipynb")
    assert model["content"].metadata["jupytext"]["formats"] == "ipynb,py:light"

    cm.save(model, path="nb.ipynb")
    assert os.path.isfile(tmp_py)
    assert read(tmp_py).metadata["jupytext"]["formats"] == "ipynb,py:light"

    time.sleep(0.5)
    del model["content"].metadata["jupytext"]["formats"]
    cm.save(model, path="nb.ipynb")
    # test that we have not kept the 'ipynb/py' pairing info, and that we can read the ipynb
    cm.get("nb.ipynb")
    os.remove(tmp_py)

    model["content"].metadata.setdefault("jupytext", {})["formats"] = "ipynb,py:percent"
    cm.save(model, path="nb.ipynb")
    assert os.path.isfile(tmp_py)
    assert read(tmp_py).metadata["jupytext"]["formats"] == "ipynb,py:percent"
    os.remove(tmp_py)

    del model["content"].metadata["jupytext"]["formats"]
    cm.save(model, path="nb.ipynb")
    assert not os.path.isfile(tmp_py)


def test_set_then_change_formats(tmpdir):
    tmp_py = str(tmpdir.join("nb.py"))
    nb = new_notebook(metadata={"jupytext": {"formats": "ipynb,py:light"}})

    cm = jupytext.TextFileContentsManager()
    cm.root_dir = str(tmpdir)

    cm.save(model=notebook_model(nb), path="nb.ipynb")
    assert os.path.isfile(tmp_py)
    assert read(tmp_py).metadata["jupytext"]["formats"] == "ipynb,py:light"
    os.remove(tmp_py)

    nb.metadata["jupytext"]["formats"] = "ipynb,py:percent"
    cm.save(model=notebook_model(nb), path="nb.ipynb")
    assert os.path.isfile(tmp_py)
    assert read(tmp_py).metadata["jupytext"]["formats"] == "ipynb,py:percent"
    os.remove(tmp_py)

    del nb.metadata["jupytext"]["formats"]
    cm.save(model=notebook_model(nb), path="nb.ipynb")
    assert not os.path.isfile(tmp_py)


@pytest.mark.parametrize("nb_file", list_notebooks("ipynb_py")[:1])
def test_set_then_change_auto_formats(tmpdir, nb_file):
    tmp_ipynb = str(tmpdir.join("nb.ipynb"))
    tmp_py = str(tmpdir.join("nb.py"))
    tmp_rmd = str(tmpdir.join("nb.Rmd"))
    nb = new_notebook(metadata=read(nb_file).metadata)

    cm = jupytext.TextFileContentsManager()
    cm.root_dir = str(tmpdir)

    # Pair ipynb/py and save
    nb.metadata["jupytext"] = {"formats": "ipynb,auto:light"}
    cm.save(model=notebook_model(nb), path="nb.ipynb")
    assert "nb.py" in cm.paired_notebooks
    assert "nb.auto" not in cm.paired_notebooks
    assert os.path.isfile(tmp_py)
    assert read(tmp_ipynb).metadata["jupytext"]["formats"] == "ipynb,py:light"

    # Pair ipynb/Rmd and save
    time.sleep(0.5)
    nb.metadata["jupytext"] = {"formats": "ipynb,Rmd"}
    cm.save(model=notebook_model(nb), path="nb.ipynb")
    assert "nb.Rmd" in cm.paired_notebooks
    assert "nb.py" not in cm.paired_notebooks
    assert "nb.auto" not in cm.paired_notebooks
    assert os.path.isfile(tmp_rmd)
    assert read(tmp_ipynb).metadata["jupytext"]["formats"] == "ipynb,Rmd"
    cm.get("nb.ipynb")

    # Unpair and save
    time.sleep(0.5)
    del nb.metadata["jupytext"]
    cm.save(model=notebook_model(nb), path="nb.ipynb")
    assert "nb.Rmd" not in cm.paired_notebooks
    assert "nb.py" not in cm.paired_notebooks
    assert "nb.auto" not in cm.paired_notebooks
    cm.get("nb.ipynb")


@pytest.mark.parametrize("nb_file", list_notebooks("ipynb_py"))
def test_share_py_recreate_ipynb(tmpdir, nb_file):
    tmp_ipynb = str(tmpdir.join("nb.ipynb"))
    tmp_py = str(tmpdir.join("nb.py"))

    cm = jupytext.TextFileContentsManager()
    cm.root_dir = str(tmpdir)

    # set default py format
    cm.preferred_jupytext_formats_save = "py:percent"

    # every new file is paired
    cm.default_jupytext_formats = "ipynb,py"

    # the text files don't need a YAML header
    cm.default_notebook_metadata_filter = "-all"
    cm.default_cell_metadata_filter = "-all"

    nb = read(nb_file)
    model_ipynb = cm.save(model=notebook_model(nb), path="nb.ipynb")

    assert os.path.isfile(tmp_ipynb)
    assert os.path.isfile(tmp_py)

    os.remove(tmp_ipynb)

    # reopen and save nb.py
    model = cm.get("nb.py")
    cm.save(model=model, path="nb.py")

    # ipynb is re-created
    assert os.path.isfile(tmp_ipynb)

    # save time of ipynb is that of py file
    assert model_ipynb["last_modified"] == model["last_modified"]


def test_vim_folding_markers(tmpdir):
    tmp_ipynb = str(tmpdir.join("nb.ipynb"))
    tmp_py = str(tmpdir.join("nb.py"))

    cm = jupytext.TextFileContentsManager()
    cm.root_dir = str(tmpdir)

    # Default Vim folding markers
    cm.default_cell_markers = "{{{,}}}"
    cm.default_jupytext_formats = "ipynb,py"

    nb = new_notebook(
        cells=[
            new_code_cell(
                """# region
'''Sample cell with region markers'''
'''End of the cell'''
# end region"""
            ),
            new_code_cell("a = 1\n\n\nb = 1"),
        ]
    )
    cm.save(model=notebook_model(nb), path="nb.ipynb")

    assert os.path.isfile(tmp_ipynb)
    assert os.path.isfile(tmp_py)

    nb2 = cm.get("nb.ipynb")["content"]
    compare_notebooks(nb2, nb)

    nb3 = read(tmp_py)
    assert nb3.metadata["jupytext"]["cell_markers"] == "{{{,}}}"

    with open(tmp_py) as fp:
        text = fp.read()

    # Remove YAML header
    text = re.sub(re.compile(r"# ---.*# ---\n\n", re.DOTALL), "", text)

    compare(
        text,
        """# region
'''Sample cell with region markers'''
'''End of the cell'''
# end region

# {{{
a = 1


b = 1
# }}}
""",
    )


def test_vscode_pycharm_folding_markers(tmpdir):
    tmp_ipynb = str(tmpdir.join("nb.ipynb"))
    tmp_py = str(tmpdir.join("nb.py"))

    cm = jupytext.TextFileContentsManager()
    cm.root_dir = str(tmpdir)

    # Default VScode/PyCharm folding markers
    cm.default_cell_markers = "region,endregion"
    cm.default_jupytext_formats = "ipynb,py"

    nb = new_notebook(
        cells=[
            new_code_cell(
                """# {{{
'''Sample cell with region markers'''
'''End of the cell'''
# }}}"""
            ),
            new_code_cell("a = 1\n\n\nb = 1"),
        ]
    )
    cm.save(model=notebook_model(nb), path="nb.ipynb")

    assert os.path.isfile(tmp_ipynb)
    assert os.path.isfile(tmp_py)

    nb2 = cm.get("nb.ipynb")["content"]
    compare_notebooks(nb2, nb)

    nb3 = read(tmp_py)
    assert nb3.metadata["jupytext"]["cell_markers"] == "region,endregion"

    with open(tmp_py) as fp:
        text = fp.read()

    # Remove YAML header
    text = re.sub(re.compile(r"# ---.*# ---\n\n", re.DOTALL), "", text)

    compare(
        text,
        """# {{{
'''Sample cell with region markers'''
'''End of the cell'''
# }}}

# region
a = 1


b = 1
# endregion
""",
    )


def test_open_file_with_default_cell_markers(tmpdir):
    tmp_py = str(tmpdir.join("nb.py"))

    cm = jupytext.TextFileContentsManager()
    cm.root_dir = str(tmpdir)

    # Default VScode/PyCharm folding markers
    cm.default_cell_markers = "region,endregion"

    text = """# +
# this is a unique code cell
1 + 1

2 + 2
"""

    with open(tmp_py, "w") as fp:
        fp.write(text)

    nb = cm.get("nb.py")["content"]
    assert len(nb.cells) == 1

    cm.save(model=notebook_model(nb), path="nb.py")

    with open(tmp_py) as fp:
        text2 = fp.read()

    expected = """# region
# this is a unique code cell
1 + 1

2 + 2
# endregion
"""

    compare(text2, expected)


def test_save_file_with_default_cell_markers(tmpdir):
    tmp_py = str(tmpdir.join("nb.py"))

    cm = jupytext.TextFileContentsManager()
    cm.root_dir = str(tmpdir)

    # Default VScode/PyCharm folding markers
    cm.default_cell_markers = "region,endregion"

    text = """# +
# this is a unique code cell
1 + 1

2 + 2
"""

    with open(tmp_py, "w") as fp:
        fp.write(text)

    nb = cm.get("nb.py")["content"]
    assert len(nb.cells) == 1

    nb.metadata["jupytext"]["cell_markers"] = "+,-"
    del nb.metadata["jupytext"]["notebook_metadata_filter"]
    cm.save(model=notebook_model(nb), path="nb.py")

    with open(tmp_py) as fp:
        text2 = fp.read()

    compare(
        "\n".join(text2.splitlines()[-len(text.splitlines()) :]),
        "\n".join(text.splitlines()),
    )

    nb2 = cm.get("nb.py")["content"]
    compare_notebooks(nb2, nb)
    assert nb2.metadata["jupytext"]["cell_markers"] == "+,-"


def test_notebook_extensions(tmpdir):
    tmp_py = str(tmpdir.join("script.py"))
    tmp_rmd = str(tmpdir.join("notebook.Rmd"))
    tmp_ipynb = str(tmpdir.join("notebook.ipynb"))

    nb = new_notebook()
    write(nb, tmp_py)
    write(nb, tmp_rmd)
    write(nb, tmp_ipynb)

    cm = jupytext.TextFileContentsManager()
    cm.root_dir = str(tmpdir)

    cm.notebook_extensions = "ipynb,Rmd"
    model = cm.get("notebook.ipynb")
    assert model["type"] == "notebook"

    model = cm.get("notebook.Rmd")
    assert model["type"] == "notebook"

    model = cm.get("script.py")
    assert model["type"] == "file"


def test_download_file_318(tmpdir):
    tmp_ipynb = str(tmpdir.join("notebook.ipynb"))
    tmp_py = str(tmpdir.join("notebook.py"))

    nb = new_notebook()
    nb.metadata["jupytext"] = {"formats": "ipynb,py"}
    write(nb, tmp_ipynb)
    write(nb, tmp_py)

    cm = jupytext.TextFileContentsManager()
    cm.root_dir = str(tmpdir)
    cm.notebook_extensions = "ipynb"

    model = cm.get("notebook.ipynb", content=True, type=None, format=None)
    assert model["type"] == "notebook"


def test_markdown_and_r_extensions(tmpdir):
    tmp_r = str(tmpdir.join("script.r"))
    tmp_markdown = str(tmpdir.join("notebook.markdown"))

    nb = new_notebook()
    write(nb, tmp_r)
    write(nb, tmp_markdown)

    cm = jupytext.TextFileContentsManager()
    cm.root_dir = str(tmpdir)

    model = cm.get("script.r")
    assert model["type"] == "notebook"

    model = cm.get("notebook.markdown")
    assert model["type"] == "notebook"


def test_server_extension_issubclass():
    class SubClassTextFileContentsManager(jupytext.TextFileContentsManager):
        pass

    assert not isinstance(
        SubClassTextFileContentsManager, jupytext.TextFileContentsManager
    )
    assert issubclass(SubClassTextFileContentsManager, jupytext.TextFileContentsManager)


def test_multiple_pairing(tmpdir):
    """Test that multiple pairing works. Input cells are loaded from the most recent text representation among
    the paired ones"""
    tmp_ipynb = str(tmpdir.join("notebook.ipynb"))
    tmp_md = str(tmpdir.join("notebook.md"))
    tmp_py = str(tmpdir.join("notebook.py"))

    def nb(text):
        return new_notebook(
            cells=[new_markdown_cell(text)],
            metadata={"jupytext": {"formats": "ipynb,md,py"}},
        )

    cm = jupytext.TextFileContentsManager()
    cm.root_dir = str(tmpdir)

    cm.save(model=notebook_model(nb("saved from cm")), path="notebook.ipynb")
    compare_notebooks(jupytext.read(tmp_ipynb), nb("saved from cm"))
    compare_notebooks(jupytext.read(tmp_md), nb("saved from cm"))
    compare_notebooks(jupytext.read(tmp_py), nb("saved from cm"))

    jupytext.write(nb("md edited"), tmp_md)
    model = cm.get("notebook.ipynb")
    compare_notebooks(model["content"], nb("md edited"))

    cm.save(model=model, path="notebook.ipynb")
    compare_notebooks(jupytext.read(tmp_ipynb), nb("md edited"))
    compare_notebooks(jupytext.read(tmp_md), nb("md edited"))
    compare_notebooks(jupytext.read(tmp_py), nb("md edited"))

    jupytext.write(nb("py edited"), tmp_py)

    # Loading the md file give the content of that file
    model = cm.get("notebook.md")
    compare_notebooks(model["content"], nb("md edited"))

    # Loading the ipynb files gives the content of the most recent text file
    model = cm.get("notebook.ipynb")
    compare_notebooks(model["content"], nb("py edited"))

    cm.save(model=model, path="notebook.ipynb")
    compare_notebooks(jupytext.read(tmp_ipynb), nb("py edited"))
    compare_notebooks(jupytext.read(tmp_md), nb("py edited"))
    compare_notebooks(jupytext.read(tmp_py), nb("py edited"))

    model_ipynb = cm.get("notebook.ipynb", content=False, load_alternative_format=False)
    model_md = cm.get("notebook.md", content=False, load_alternative_format=False)
    model_py = cm.get("notebook.py", content=False, load_alternative_format=False)

    # ipynb is the oldest one, then py, then md
    # so that we read cell inputs from the py file
    assert model_ipynb["last_modified"] <= model_py["last_modified"]
    assert model_py["last_modified"] <= model_md["last_modified"]


@skip_if_dict_is_not_ordered
@pytest.mark.parametrize("nb_file", list_notebooks("ipynb_py"))
def test_filter_jupytext_version_information_416(nb_file, tmpdir):
    tmp_py = str(tmpdir.join("notebook.py"))

    cm = jupytext.TextFileContentsManager()
    cm.root_dir = str(tmpdir)
    cm.default_notebook_metadata_filter = (
        "-jupytext.text_representation.jupytext_version"
    )

    # load notebook
    notebook = jupytext.read(nb_file)
    notebook.metadata["jupytext_formats"] = "ipynb,py"
    model = notebook_model(notebook)

    # save to ipynb and py
    cm.save(model=model, path="notebook.ipynb")

    assert os.path.isfile(tmp_py)

    # read py file
    with open(tmp_py) as fp:
        text = fp.read()

    assert "---" in text
    assert "jupytext:" in text
    assert "kernelspec:" in text
    assert "jupytext_version:" not in text


def test_new_untitled(tmpdir):
    cm = jupytext.TextFileContentsManager()
    cm.root_dir = str(tmpdir)

    # untitled is "Untitled" only when the locale is English #636
    untitled, ext = cm.new_untitled(type="notebook")["path"].split(".")
    assert untitled
    assert ext == "ipynb"

    assert cm.new_untitled(type="notebook", ext=".md")["path"] == untitled + "1.md"
    assert cm.new_untitled(type="notebook", ext=".py")["path"] == untitled + "2.py"
    assert cm.new_untitled(type="notebook")["path"] == untitled + "3.ipynb"
    assert (
        cm.new_untitled(type="notebook", ext=".py:percent")["path"] == untitled + "4.py"
    )


def test_nested_prefix(tmpdir):
    cm = jupytext.TextFileContentsManager()
    cm.root_dir = str(tmpdir)

    # save to ipynb and py
    nb = new_notebook(
        cells=[new_code_cell("1+1"), new_markdown_cell("Some text")],
        metadata={"jupytext": {"formats": "ipynb,nested/prefix//.py"}},
    )
    cm.save(model=notebook_model(nb), path="notebook.ipynb")

    assert tmpdir.join("nested").join("prefix").join("notebook.py").isfile()


def fs_meta_manager(tmpdir):
    try:
        from jupyterfs.metamanager import MetaManager
    except ImportError:
        pytest.skip("jupyterfs is not available")

    cm_class = jupytext.build_jupytext_contents_manager_class(MetaManager)
    logger = logging.getLogger("jupyter-fs")
    cm = cm_class(parent=None, log=logger)
    cm.initResource(
        {
            "url": "osfs://{}".format(tmpdir),
        }
    )
    return cm


def test_jupytext_jupyter_fs_metamanager(tmpdir):
    """Test the basic get/save functions of Jupytext with a fs manager
    https://github.com/mwouts/jupytext/issues/618"""
    cm = fs_meta_manager(tmpdir)
    # the hash that corresponds to the osfs
    osfs = [h for h in cm._managers if h != ""][0]

    # save a few files
    text = "some text\n"
    cm.save(dict(type="file", content=text, format="text"), path=osfs + ":text.md")
    nb = new_notebook(
        cells=[new_markdown_cell("A markdown cell"), new_code_cell("1 + 1")]
    )
    cm.save(notebook_model(nb), osfs + ":notebook.ipynb")
    cm.save(notebook_model(nb), osfs + ":text_notebook.md")

    # list the directory
    directory = cm.get(osfs + ":/")
    assert set(file["name"] for file in directory["content"]) == {
        "text.md",
        "text_notebook.md",
        "notebook.ipynb",
    }

    # get the files
    model = cm.get(osfs + ":/text.md", type="file")
    assert model["type"] == "file"
    assert model["content"] == text

    model = cm.get(osfs + ":text.md", type="notebook")
    assert model["type"] == "notebook"
    # We only compare the cells, as kernelspecs are added to the notebook metadata
    compare(model["content"].cells, [new_markdown_cell(text.strip())])

    for nb_file in ["notebook.ipynb", "text_notebook.md"]:
        model = cm.get(osfs + ":" + nb_file)
        assert model["type"] == "notebook"
        actual_cells = model["content"].cells

        # saving adds 'trusted=True' to the code cell metadata
        for cell in actual_cells:
            cell.metadata = {}
        compare(actual_cells, nb.cells)


def test_config_jupytext_jupyter_fs_meta_manager(tmpdir):
    """Test the configuration of Jupytext with a fs manager"""
    tmpdir.join("jupytext.toml").write('default_jupytext_formats = "ipynb,py"')
    cm = fs_meta_manager(tmpdir)
    # the hash that corresponds to the osfs
    osfs = [h for h in cm._managers if h != ""][0]

    # save a few files
    nb = new_notebook()
    cm.save(dict(type="file", content="text", format="text"), path=osfs + ":text.md")
    cm.save(notebook_model(nb), osfs + ":script.py")
    cm.save(notebook_model(nb), osfs + ":text_notebook.md")
    cm.save(notebook_model(nb), osfs + ":notebook.ipynb")

    # list the directory
    directory = cm.get(osfs + ":/")
    assert set(file["name"] for file in directory["content"]) == {
        "jupytext.toml",
        "text.md",
        "text_notebook.md",
        "notebook.ipynb",
        "notebook.py",
        "script.py",
        "script.ipynb",
    }
