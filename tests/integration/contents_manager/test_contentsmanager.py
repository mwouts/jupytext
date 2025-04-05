import inspect
import os
import re
import shutil
import time

import pytest
from jupyter_server.utils import ensure_async
from nbformat.v4.nbbase import new_code_cell, new_markdown_cell, new_notebook
from tornado.web import HTTPError

import jupytext
from jupytext.cli import jupytext as jupytext_cli
from jupytext.compare import compare, compare_notebooks, notebook_model
from jupytext.formats import auto_ext_from_metadata, read_format_from_metadata
from jupytext.header import header_to_metadata_and_cell
from jupytext.jupytext import read, write, writes
from jupytext.kernels import kernelspec_from_language

pytestmark = pytest.mark.asyncio


async def test_rename(tmpdir, cm):
    org_file = str(tmpdir.join("notebook.ipynb"))
    new_file = str(tmpdir.join("new.ipynb"))
    jupytext.write(new_notebook(), org_file)

    cm.root_dir = str(tmpdir)
    await ensure_async(cm.rename_file("notebook.ipynb", "new.ipynb"))

    assert os.path.isfile(new_file)
    assert not os.path.isfile(org_file)


async def test_rename_inconsistent_path(tmpdir, cm):
    org_file = str(tmpdir.join("notebook_suffix.ipynb"))
    new_file = str(tmpdir.join("new.ipynb"))
    jupytext.write(
        new_notebook(metadata={"jupytext": {"formats": "_suffix.ipynb"}}), org_file
    )

    cm.root_dir = str(tmpdir)
    # Read notebook, and learn about its format
    await ensure_async(cm.get("notebook_suffix.ipynb"))
    with pytest.raises(HTTPError):
        await ensure_async(cm.rename_file("notebook_suffix.ipynb", "new.ipynb"))

    assert not os.path.isfile(new_file)
    assert os.path.isfile(org_file)


async def test_pair_unpair_notebook(tmpdir, cm):
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

    cm.root_dir = str(tmpdir)

    # save notebook
    await ensure_async(cm.save(model=notebook_model(nb), path=tmp_ipynb))
    assert not os.path.isfile(str(tmpdir.join(tmp_md)))

    # pair notebook
    nb["metadata"]["jupytext"] = {"formats": "ipynb,md"}
    await ensure_async(cm.save(model=notebook_model(nb), path=tmp_ipynb))
    assert os.path.isfile(str(tmpdir.join(tmp_md)))

    # reload and get outputs
    nb2 = (await ensure_async(cm.get(tmp_md)))["content"]
    compare_notebooks(nb, nb2)

    # unpair and save as md
    del nb["metadata"]["jupytext"]
    await ensure_async(cm.save(model=notebook_model(nb), path=tmp_md))
    nb2 = (await ensure_async(cm.get(tmp_md)))["content"]

    # we get no outputs here
    compare_notebooks(nb, nb2, compare_outputs=False)
    assert len(nb2.cells[0]["outputs"]) == 0


async def test_load_save_rename(ipynb_py_R_jl_file, cm, tmpdir):
    tmp_ipynb = "notebook.ipynb"
    tmp_rmd = "notebook.Rmd"

    cm.formats = "ipynb,Rmd"
    cm.root_dir = str(tmpdir)
    cm.delete_to_trash = False

    # open ipynb, save Rmd, reopen
    nb = jupytext.read(ipynb_py_R_jl_file)
    await ensure_async(cm.save(model=notebook_model(nb), path=tmp_rmd))
    nb_rmd = await ensure_async(cm.get(tmp_rmd))
    compare_notebooks(nb_rmd["content"], nb, "Rmd")

    # save ipynb
    await ensure_async(cm.save(model=notebook_model(nb), path=tmp_ipynb))

    # rename_file ipynb
    await ensure_async(cm.rename_file(tmp_ipynb, "new.ipynb"))
    assert not os.path.isfile(str(tmpdir.join(tmp_ipynb)))
    assert not os.path.isfile(str(tmpdir.join(tmp_rmd)))

    assert os.path.isfile(str(tmpdir.join("new.ipynb")))
    assert os.path.isfile(str(tmpdir.join("new.Rmd")))

    # delete one file, test that we can still read and rename_file it
    await ensure_async(cm.delete("new.Rmd"))
    assert not os.path.isfile(str(tmpdir.join("new.Rmd")))
    model = await ensure_async(cm.get("new.ipynb", content=False))
    assert "last_modified" in model
    await ensure_async(cm.save(model=notebook_model(nb), path="new.ipynb"))
    assert os.path.isfile(str(tmpdir.join("new.Rmd")))

    await ensure_async(cm.delete("new.Rmd"))
    await ensure_async(cm.rename_file("new.ipynb", tmp_ipynb))

    assert os.path.isfile(str(tmpdir.join(tmp_ipynb)))
    assert not os.path.isfile(str(tmpdir.join(tmp_rmd)))
    assert not os.path.isfile(str(tmpdir.join("new.ipynb")))
    assert not os.path.isfile(str(tmpdir.join("new.Rmd")))


async def test_save_load_paired_md_notebook(ipynb_py_R_jl_file, cm, tmpdir):
    tmp_ipynb = "notebook.ipynb"
    tmp_md = "notebook.md"

    cm.root_dir = str(tmpdir)

    # open ipynb, save with cm, reopen
    nb = jupytext.read(ipynb_py_R_jl_file)
    nb.metadata["jupytext"] = {"formats": "ipynb,md"}

    await ensure_async(cm.save(model=notebook_model(nb), path=tmp_ipynb))
    nb_md = await ensure_async(cm.get(tmp_md))

    compare_notebooks(nb_md["content"], nb, "md")
    assert nb_md["content"].metadata["jupytext"]["formats"] == "ipynb,md"


async def test_pair_plain_script(percent_file, cm, tmpdir, caplog):
    tmp_py = "notebook.py"
    tmp_ipynb = "notebook.ipynb"

    cm.root_dir = str(tmpdir)

    # open py file, pair, save with cm
    nb = jupytext.read(percent_file)
    nb.metadata["jupytext"]["formats"] = "ipynb,py:hydrogen"
    await ensure_async(cm.save(model=notebook_model(nb), path=tmp_py))

    # assert "'Include Metadata' is off" in caplog.text

    assert os.path.isfile(str(tmpdir.join(tmp_py)))
    assert os.path.isfile(str(tmpdir.join(tmp_ipynb)))

    # Make sure we've not changed the script
    with open(percent_file) as fp:
        script = fp.read()

    with open(str(tmpdir.join(tmp_py))) as fp:
        script2 = fp.read()

    compare(script2, script)

    # reopen py file with the cm
    nb2 = (await ensure_async(cm.get(tmp_py)))["content"]
    compare_notebooks(nb2, nb)
    assert nb2.metadata["jupytext"]["formats"] == "ipynb,py:hydrogen"

    # remove the pairing and save
    del nb.metadata["jupytext"]["formats"]
    await ensure_async(cm.save(model=notebook_model(nb), path=tmp_py))

    # reopen py file with the cm
    nb2 = (await ensure_async(cm.get(tmp_py)))["content"]
    compare_notebooks(nb2, nb)
    assert "formats" not in nb2.metadata["jupytext"]


async def test_load_save_rename_nbpy(ipynb_py_file, cm, tmpdir):
    tmp_ipynb = "notebook.ipynb"
    tmp_nbpy = "notebook.nb.py"

    cm.formats = "ipynb,.nb.py"
    cm.root_dir = str(tmpdir)

    # open ipynb, save nb.py, reopen
    nb = jupytext.read(ipynb_py_file)
    await ensure_async(cm.save(model=notebook_model(nb), path=tmp_nbpy))
    nbpy = await ensure_async(cm.get(tmp_nbpy))
    compare_notebooks(nbpy["content"], nb)

    # save ipynb
    await ensure_async(cm.save(model=notebook_model(nb), path=tmp_ipynb))

    # rename_file nbpy
    await ensure_async(cm.rename_file(tmp_nbpy, "new.nb.py"))
    assert not os.path.isfile(str(tmpdir.join(tmp_ipynb)))
    assert not os.path.isfile(str(tmpdir.join(tmp_nbpy)))

    assert os.path.isfile(str(tmpdir.join("new.ipynb")))
    assert os.path.isfile(str(tmpdir.join("new.nb.py")))

    # rename_file to a non-matching pattern
    with pytest.raises(HTTPError):
        await ensure_async(cm.rename_file(tmp_nbpy, "suffix_missing.py"))


async def test_load_save_py_freeze_metadata(python_file, cm, tmpdir):
    if "light" in python_file:
        pytest.skip()

    tmp_nbpy = "notebook.py"

    cm.root_dir = str(tmpdir)

    # read original file
    with open(python_file) as fp:
        text_py = fp.read()

    # write to tmp_nbpy
    with open(str(tmpdir.join(tmp_nbpy)), "w") as fp:
        fp.write(text_py)

    # open and save notebook
    nb = (await ensure_async(cm.get(tmp_nbpy)))["content"]
    await ensure_async(cm.save(model=notebook_model(nb), path=tmp_nbpy))

    with open(str(tmpdir.join(tmp_nbpy))) as fp:
        text_py2 = fp.read()

    compare(text_py2, text_py)


async def test_load_text_notebook(tmpdir, cm):
    cm.root_dir = str(tmpdir)

    nbpy = "text.py"
    with open(str(tmpdir.join(nbpy)), "w") as fp:
        fp.write("# %%\n1 + 1\n")

    py_model = await ensure_async(cm.get(nbpy, content=False))
    assert py_model["type"] == "notebook"
    assert py_model["content"] is None

    py_model = await ensure_async(cm.get(nbpy, content=True))
    assert py_model["type"] == "notebook"
    assert "cells" in py_model["content"]

    # The model returned by the CM should match that of a classical ipynb notebook
    nb_model = dict(
        type="notebook", content=new_notebook(cells=[new_markdown_cell("A cell")])
    )
    await ensure_async(cm.save(nb_model, "notebook.ipynb"))
    nb_model = await ensure_async(cm.get("notebook.ipynb", content=True))
    for key in ["format", "mimetype", "type"]:
        assert nb_model[key] == py_model[key], key


async def test_load_save_rename_notebook_with_dot(ipynb_py_file, cm, tmpdir):
    tmp_ipynb = "1.notebook.ipynb"
    tmp_nbpy = "1.notebook.py"

    cm.formats = "ipynb,py"
    cm.root_dir = str(tmpdir)

    # open ipynb, save nb.py, reopen
    nb = jupytext.read(ipynb_py_file)
    await ensure_async(cm.save(model=notebook_model(nb), path=tmp_nbpy))
    nbpy = await ensure_async(cm.get(tmp_nbpy))
    compare_notebooks(nbpy["content"], nb)

    # save ipynb
    await ensure_async(cm.save(model=notebook_model(nb), path=tmp_ipynb))

    # rename_file py
    await ensure_async(cm.rename_file(tmp_nbpy, "2.new_notebook.py"))
    assert not os.path.isfile(str(tmpdir.join(tmp_ipynb)))
    assert not os.path.isfile(str(tmpdir.join(tmp_nbpy)))

    assert os.path.isfile(str(tmpdir.join("2.new_notebook.ipynb")))
    assert os.path.isfile(str(tmpdir.join("2.new_notebook.py")))


async def test_load_save_rename_nbpy_default_config(ipynb_py_file, cm, tmpdir):
    tmp_ipynb = "notebook.ipynb"
    tmp_nbpy = "notebook.nb.py"

    cm.formats = "ipynb,.nb.py"
    cm.root_dir = str(tmpdir)

    # open ipynb, save nb.py, reopen
    nb = jupytext.read(ipynb_py_file)

    await ensure_async(cm.save(model=notebook_model(nb), path=tmp_nbpy))
    nbpy = await ensure_async(cm.get(tmp_nbpy))
    compare_notebooks(nbpy["content"], nb)

    # open ipynb
    nbipynb = await ensure_async(cm.get(tmp_ipynb))
    compare_notebooks(nbipynb["content"], nb)

    # save ipynb
    await ensure_async(cm.save(model=notebook_model(nb), path=tmp_ipynb))

    # rename_file notebook.nb.py to new.nb.py
    await ensure_async(cm.rename_file(tmp_nbpy, "new.nb.py"))
    assert not os.path.isfile(str(tmpdir.join(tmp_ipynb)))
    assert not os.path.isfile(str(tmpdir.join(tmp_nbpy)))

    assert os.path.isfile(str(tmpdir.join("new.ipynb")))
    assert os.path.isfile(str(tmpdir.join("new.nb.py")))

    # rename_file new.ipynb to notebook.ipynb
    await ensure_async(cm.rename_file("new.ipynb", tmp_ipynb))
    assert os.path.isfile(str(tmpdir.join(tmp_ipynb)))
    assert os.path.isfile(str(tmpdir.join(tmp_nbpy)))

    assert not os.path.isfile(str(tmpdir.join("new.ipynb")))
    assert not os.path.isfile(str(tmpdir.join("new.nb.py")))


async def test_load_save_rename_non_ascii_path(ipynb_py_file, cm, tmpdir):
    tmp_ipynb = "notebôk.ipynb"
    tmp_nbpy = "notebôk.nb.py"

    cm.formats = "ipynb,.nb.py"
    tmpdir = "" + str(tmpdir)
    cm.root_dir = tmpdir

    # open ipynb, save nb.py, reopen
    nb = jupytext.read(ipynb_py_file)

    await ensure_async(cm.save(model=notebook_model(nb), path=tmp_nbpy))
    nbpy = await ensure_async(cm.get(tmp_nbpy))
    compare_notebooks(nbpy["content"], nb)

    # open ipynb
    nbipynb = await ensure_async(cm.get(tmp_ipynb))
    compare_notebooks(nbipynb["content"], nb)

    # save ipynb
    await ensure_async(cm.save(model=notebook_model(nb), path=tmp_ipynb))

    # rename_file notebôk.nb.py to nêw.nb.py
    await ensure_async(cm.rename_file(tmp_nbpy, "nêw.nb.py"))
    assert not os.path.isfile(os.path.join(tmpdir, tmp_ipynb))
    assert not os.path.isfile(os.path.join(tmpdir, tmp_nbpy))

    assert os.path.isfile(os.path.join(tmpdir, "nêw.ipynb"))
    assert os.path.isfile(os.path.join(tmpdir, "nêw.nb.py"))

    # rename_file nêw.ipynb to notebôk.ipynb
    await ensure_async(cm.rename_file("nêw.ipynb", tmp_ipynb))
    assert os.path.isfile(os.path.join(tmpdir, tmp_ipynb))
    assert os.path.isfile(os.path.join(tmpdir, tmp_nbpy))

    assert not os.path.isfile(os.path.join(tmpdir, "nêw.ipynb"))
    assert not os.path.isfile(os.path.join(tmpdir, "nêw.nb.py"))


async def test_outdated_text_notebook(python_notebook, cm, tmpdir):
    # 1. write py ipynb
    cm.formats = "py,ipynb"
    cm.outdated_text_notebook_margin = 0
    cm.root_dir = str(tmpdir)

    # open ipynb, save py, reopen
    nb = python_notebook
    await ensure_async(cm.save(model=notebook_model(nb), path="notebook.py"))
    model_py = await ensure_async(cm.get("notebook.py", load_alternative_format=False))
    model_ipynb = await ensure_async(
        cm.get("notebook.ipynb", load_alternative_format=False)
    )

    # 2. check that time of ipynb <= py
    assert model_ipynb["last_modified"] <= model_py["last_modified"]

    # 3. wait some time
    time.sleep(0.5)

    # 4. modify ipynb
    nb.cells.append(new_markdown_cell("New cell"))
    write(nb, str(tmpdir.join("notebook.ipynb")))

    # 5. test error
    with pytest.raises(HTTPError):
        await ensure_async(cm.get("notebook.py"))

    # 6. test OK with
    cm.outdated_text_notebook_margin = 1.0
    await ensure_async(cm.get("notebook.py"))

    # 7. test OK with
    cm.outdated_text_notebook_margin = float("inf")
    await ensure_async(cm.get("notebook.py"))


async def test_outdated_text_notebook_no_diff_ok(tmpdir, cm, python_notebook):
    # 1. write py ipynb
    cm.formats = "py,ipynb"
    cm.outdated_text_notebook_margin = 0
    cm.root_dir = str(tmpdir)

    # open ipynb, save py, reopen
    nb = python_notebook
    await ensure_async(cm.save(model=notebook_model(nb), path="notebook.py"))
    model_py = await ensure_async(cm.get("notebook.py", load_alternative_format=False))
    model_ipynb = await ensure_async(
        cm.get("notebook.ipynb", load_alternative_format=False)
    )

    # 2. check that time of ipynb <= py
    assert model_ipynb["last_modified"] <= model_py["last_modified"]

    # 3. wait some time
    time.sleep(0.5)

    # 4. touch ipynb
    with open(tmpdir / "notebook.ipynb", "a"):
        os.utime(tmpdir / "notebook.ipynb", None)

    # 5. No error since both files correspond to the same notebook #799
    await ensure_async(cm.get("notebook.py"))


async def test_outdated_text_notebook_diff_is_shown(tmpdir, cm, python_notebook):
    # 1. write py ipynb
    cm.formats = "py,ipynb"
    cm.outdated_text_notebook_margin = 0
    cm.root_dir = str(tmpdir)

    # open ipynb, save py, reopen
    nb = python_notebook
    nb.cells = [new_markdown_cell("Text version 1.0")]
    await ensure_async(cm.save(model=notebook_model(nb), path="notebook.py"))
    model_py = await ensure_async(cm.get("notebook.py", load_alternative_format=False))
    model_ipynb = await ensure_async(
        cm.get("notebook.ipynb", load_alternative_format=False)
    )

    # 2. check that time of ipynb <= py
    assert model_ipynb["last_modified"] <= model_py["last_modified"]

    # 3. wait some time
    time.sleep(0.5)

    # 4. modify ipynb
    nb.cells = [new_markdown_cell("Text version 2.0")]
    jupytext.write(nb, str(tmpdir / "notebook.ipynb"))

    # 5. The diff is shown in the error
    with pytest.raises(HTTPError) as excinfo:
        await ensure_async(cm.get("notebook.py"))

    diff = excinfo.value.log_message

    diff = diff[diff.find("Differences") : diff.rfind("Please")]

    compare(
        # In the reference below, lines with a single space
        # have been stripped by the pre-commit hook
        diff.replace("\n \n", "\n\n"),
        """Differences (jupytext --diff notebook.py notebook.ipynb) are:
--- notebook.py
+++ notebook.ipynb
@@ -13,5 +13,5 @@
 # ---

 # %%%% [markdown]
-# Text version 1.0
+# Text version 2.0

""",
    )


async def test_reload_notebook_after_jupytext_cli(python_notebook, cm, tmpdir):
    tmp_ipynb = str(tmpdir.join("notebook.ipynb"))
    tmp_nbpy = str(tmpdir.join("notebook.py"))

    cm.outdated_text_notebook_margin = 0
    cm.root_dir = str(tmpdir)

    # write the paired notebook
    nb = python_notebook
    nb.metadata.setdefault("jupytext", {})["formats"] = "py,ipynb"
    await ensure_async(cm.save(model=notebook_model(nb), path="notebook.py"))

    assert os.path.isfile(tmp_ipynb)
    assert os.path.isfile(tmp_nbpy)

    # run jupytext CLI
    jupytext_cli([tmp_nbpy, "--to", "ipynb", "--update"])

    # test reload
    nb1 = (await ensure_async(cm.get("notebook.py")))["content"]
    nb2 = (await ensure_async(cm.get("notebook.ipynb")))["content"]

    compare_notebooks(nb, nb1)
    compare_notebooks(nb, nb2)


async def test_load_save_percent_format(percent_file, cm, tmpdir):
    tmp_py = "notebook.py"
    with open(percent_file) as stream:
        text_py = stream.read()
    with open(str(tmpdir.join(tmp_py)), "w") as stream:
        stream.write(text_py)

    cm.root_dir = str(tmpdir)

    # open python, save
    nb = (await ensure_async(cm.get(tmp_py)))["content"]
    del nb.metadata["jupytext"]["notebook_metadata_filter"]
    await ensure_async(cm.save(model=notebook_model(nb), path=tmp_py))

    # compare the new file with original one
    with open(str(tmpdir.join(tmp_py))) as stream:
        text_py2 = stream.read()

    # do we find 'percent' in the header?
    header = text_py2[: -len(text_py)]
    assert any(["percent" in line for line in header.splitlines()])

    # Remove the YAML header
    text_py2 = text_py2[-len(text_py) :]

    compare(text_py2, text_py)


async def test_save_to_percent_format(ipynb_julia_file, cm, tmpdir):
    tmp_ipynb = "notebook.ipynb"
    tmp_jl = "notebook.jl"

    cm.root_dir = str(tmpdir)
    cm.preferred_jupytext_formats_save = "jl:percent"

    nb = jupytext.read(ipynb_julia_file)
    nb["metadata"]["jupytext"] = {"formats": "ipynb,jl"}

    # save to ipynb and jl
    await ensure_async(cm.save(model=notebook_model(nb), path=tmp_ipynb))

    # read jl file
    with open(str(tmpdir.join(tmp_jl))) as stream:
        text_jl = stream.read()

    # Parse the YAML header
    metadata, _, _, _ = header_to_metadata_and_cell(text_jl.splitlines(), "#", "")
    assert metadata["jupytext"]["formats"] == "ipynb,jl:percent"


async def test_save_using_preferred_and_default_format_170(ipynb_py_file, cm, tmpdir):
    nb = read(ipynb_py_file)

    # Way 0: preferred_jupytext_formats_save, no prefix + formats
    tmp_py = str(tmpdir.join("python/notebook.py"))

    cm.root_dir = str(tmpdir)
    cm.preferred_jupytext_formats_save = "py:percent"
    cm.formats = "ipynb,python//py"

    # save to ipynb and py
    await ensure_async(cm.save(model=notebook_model(nb), path="notebook.ipynb"))

    # read py file
    nb_py = read(tmp_py)
    assert nb_py.metadata["jupytext"]["text_representation"]["format_name"] == "percent"

    # Way 1: preferred_jupytext_formats_save + formats
    tmp_py = str(tmpdir.join("python/notebook.py"))

    cm.root_dir = str(tmpdir)
    cm.preferred_jupytext_formats_save = "python//py:percent"
    cm.formats = "ipynb,python//py"

    # save to ipynb and py
    await ensure_async(cm.save(model=notebook_model(nb), path="notebook.ipynb"))

    # read py file
    nb_py = read(tmp_py)
    assert nb_py.metadata["jupytext"]["text_representation"]["format_name"] == "percent"

    # Way 2: formats
    tmp_py = str(tmpdir.join("python/notebook.py"))

    cm.root_dir = str(tmpdir)
    cm.formats = "ipynb,python//py:percent"

    # save to ipynb and py
    await ensure_async(cm.save(model=notebook_model(nb), path="notebook.ipynb"))

    # read py file
    nb_py = read(tmp_py)
    assert nb_py.metadata["jupytext"]["text_representation"]["format_name"] == "percent"


async def test_open_using_preferred_and_default_format_174(ipynb_py_file, cm, tmpdir):
    tmp_ipynb = str(tmpdir.join("notebook.ipynb"))
    tmp_py = str(tmpdir.join("python/notebook.py"))
    tmp_py2 = str(tmpdir.join("other/notebook.py"))
    os.makedirs(str(tmpdir.join("other")))
    shutil.copyfile(ipynb_py_file, tmp_ipynb)

    cm.root_dir = str(tmpdir)
    cm.formats = "ipynb,python//py:percent"
    cm.notebook_metadata_filter = "all"
    cm.cell_metadata_filter = "all"

    # load notebook
    model = await ensure_async(cm.get("notebook.ipynb"))

    # save to ipynb and py
    await ensure_async(cm.save(model=model, path="notebook.ipynb"))

    assert os.path.isfile(tmp_py)
    os.remove(tmp_ipynb)

    # read py file
    model2 = await ensure_async(cm.get("python/notebook.py"))
    compare_notebooks(model2["content"], model["content"])

    # move py file to the another folder
    shutil.move(tmp_py, tmp_py2)
    model2 = await ensure_async(cm.get("other/notebook.py"))
    compare_notebooks(model2["content"], model["content"])
    await ensure_async(cm.save(model=model, path="other/notebook.py"))
    assert not os.path.isfile(tmp_ipynb)
    assert not os.path.isfile(str(tmpdir.join("other/notebook.ipynb")))


async def test_kernelspec_are_preserved(ipynb_py_file, cm, tmpdir):
    if "many hash" in ipynb_py_file:
        pytest.skip()
    tmp_ipynb = str(tmpdir.join("notebook.ipynb"))
    tmp_py = str(tmpdir.join("notebook.py"))
    shutil.copyfile(ipynb_py_file, tmp_ipynb)

    cm.root_dir = str(tmpdir)
    cm.formats = "ipynb,py"
    cm.notebook_metadata_filter = "-all"

    # load notebook
    model = await ensure_async(cm.get("notebook.ipynb"))
    model["content"].metadata["kernelspec"] = {
        "display_name": "Kernel name",
        "language": "python",
        "name": "custom",
    }

    # save to ipynb and py
    await ensure_async(cm.save(model=model, path="notebook.ipynb"))
    assert os.path.isfile(tmp_py)

    # read ipynb
    model2 = await ensure_async(cm.get("notebook.ipynb"))
    compare_notebooks(model2["content"], model["content"])


async def test_save_to_light_percent_sphinx_format(ipynb_py_file, cm, tmpdir):
    tmp_ipynb = "notebook.ipynb"
    tmp_lgt_py = "notebook.lgt.py"
    tmp_pct_py = "notebook.pct.py"
    tmp_spx_py = "notebook.spx.py"

    cm.root_dir = str(tmpdir)

    nb = jupytext.read(ipynb_py_file)
    nb["metadata"]["jupytext"] = {
        "formats": "ipynb,.pct.py:percent,.lgt.py:light,.spx.py:sphinx"
    }

    # save to ipynb and three python flavors
    await ensure_async(cm.save(model=notebook_model(nb), path=tmp_ipynb))

    # read files
    with open(str(tmpdir.join(tmp_pct_py))) as stream:
        assert read_format_from_metadata(stream.read(), ".py") == "percent"

    with open(str(tmpdir.join(tmp_lgt_py))) as stream:
        assert read_format_from_metadata(stream.read(), ".py") == "light"

    with open(str(tmpdir.join(tmp_spx_py))) as stream:
        assert read_format_from_metadata(stream.read(), ".py") == "sphinx"

    model = await ensure_async(cm.get(path=tmp_pct_py))
    compare_notebooks(model["content"], nb)

    model = await ensure_async(cm.get(path=tmp_lgt_py))
    compare_notebooks(model["content"], nb)

    model = await ensure_async(cm.get(path=tmp_spx_py))
    # (notebooks not equal as we insert %matplotlib inline in sphinx)

    model = await ensure_async(cm.get(path=tmp_ipynb))
    compare_notebooks(model["content"], nb)


async def test_pair_notebook_with_dot(ipynb_py_file, cm, tmpdir):
    # Reproduce issue #138
    tmp_py = "file.5.1.py"
    tmp_ipynb = "file.5.1.ipynb"

    cm.root_dir = str(tmpdir)

    nb = jupytext.read(ipynb_py_file)
    nb["metadata"]["jupytext"] = {"formats": "ipynb,py:percent"}

    # save to ipynb and three python flavors
    await ensure_async(cm.save(model=notebook_model(nb), path=tmp_ipynb))

    assert os.path.isfile(str(tmpdir.join(tmp_ipynb)))

    # read files
    with open(str(tmpdir.join(tmp_py))) as stream:
        assert read_format_from_metadata(stream.read(), ".py") == "percent"

    model = await ensure_async(cm.get(path=tmp_py))
    assert model["name"] == "file.5.1.py"
    compare_notebooks(model["content"], nb)

    model = await ensure_async(cm.get(path=tmp_ipynb))
    assert model["name"] == "file.5.1.ipynb"
    compare_notebooks(model["content"], nb)


async def test_preferred_format_allows_to_read_others_format(
    python_notebook, cm, tmpdir
):
    # 1. write py ipynb
    tmp_ipynb = "notebook.ipynb"
    tmp_nbpy = "notebook.py"

    cm.preferred_jupytext_formats_save = "py:light"
    cm.root_dir = str(tmpdir)

    # load notebook and save it using the cm
    nb = python_notebook
    nb["metadata"]["jupytext"] = {"formats": "ipynb,py"}
    await ensure_async(cm.save(model=notebook_model(nb), path=tmp_ipynb))

    # Saving does not update the metadata, as 'save' makes a copy of the notebook
    # assert nb['metadata']['jupytext']['formats'] == 'ipynb,py:light'

    # Set preferred format for reading
    cm.preferred_jupytext_formats_read = "py:percent"

    # Read notebook
    model = await ensure_async(cm.get(tmp_nbpy))

    # Check that format is explicit
    assert model["content"]["metadata"]["jupytext"]["formats"] == "ipynb,py:light"

    # Check contents
    compare_notebooks(model["content"], nb)

    # Change save format and save
    model["content"]["metadata"]["jupytext"]["formats"] == "ipynb,py"
    cm.preferred_jupytext_formats_save = "py:percent"
    await ensure_async(cm.save(model=notebook_model(nb), path=tmp_ipynb))

    # Read notebook
    model = await ensure_async(cm.get(tmp_nbpy))
    compare_notebooks(model["content"], nb)

    # Check that format is explicit
    assert model["content"]["metadata"]["jupytext"]["formats"] == "ipynb,py:percent"


async def test_preferred_formats_read_auto(tmpdir, cm):
    tmp_py = "notebook.py"
    with open(str(tmpdir.join(tmp_py)), "w") as script:
        script.write(
            """# cell one
1 + 1
"""
        )

    # create contents manager with default load format as percent
    cm.preferred_jupytext_formats_read = "auto:percent"
    cm.root_dir = str(tmpdir)

    # load notebook
    model = await ensure_async(cm.get(tmp_py))

    # check that script is opened as percent
    assert (
        "percent"
        == model["content"]["metadata"]["jupytext"]["text_representation"][
            "format_name"
        ]
    )


async def test_save_in_auto_extension_global(ipynb_py_R_jl_file, cm, tmpdir):
    # load notebook
    nb = jupytext.read(ipynb_py_R_jl_file)

    auto_ext = auto_ext_from_metadata(nb.metadata)
    tmp_ipynb = "notebook.ipynb"
    tmp_script = "notebook" + auto_ext

    # create contents manager with default load format as percent
    cm.formats = "ipynb,auto"
    cm.preferred_jupytext_formats_save = "auto:percent"
    cm.root_dir = str(tmpdir)

    # save notebook
    await ensure_async(cm.save(model=notebook_model(nb), path=tmp_ipynb))

    # check that text representation exists, and is in percent format
    with open(str(tmpdir.join(tmp_script))) as stream:
        assert read_format_from_metadata(stream.read(), auto_ext) == "percent"

    # reload and compare with original notebook
    model = await ensure_async(cm.get(path=tmp_script))

    # saving should not create a format entry #95
    assert "formats" not in model["content"].metadata.get("jupytext", {})

    compare_notebooks(model["content"], nb)


async def test_global_auto_pairing_works_with_empty_notebook(tmpdir, cm):
    nb = new_notebook()
    tmp_ipynb = str(tmpdir.join("notebook.ipynb"))
    tmp_py = str(tmpdir.join("notebook.py"))
    tmp_auto = str(tmpdir.join("notebook.auto"))

    # create contents manager with default load format as percent
    cm.formats = "ipynb,auto"
    cm.preferred_jupytext_formats_save = "auto:percent"
    cm.root_dir = str(tmpdir)

    # save notebook
    await ensure_async(cm.save(model=notebook_model(nb), path="notebook.ipynb"))

    # check that only the ipynb representation exists
    assert os.path.isfile(tmp_ipynb)
    assert not os.path.isfile(tmp_py)
    assert not os.path.isfile(tmp_auto)
    assert "notebook.ipynb" not in cm.paired_notebooks

    model = await ensure_async(cm.get(path="notebook.ipynb"))
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
    await ensure_async(cm.save(model=notebook_model(nb), path="notebook.ipynb"))

    # check that ipynb + py representations exists
    assert os.path.isfile(tmp_ipynb)
    assert os.path.isfile(tmp_py)
    assert not os.path.isfile(tmp_auto)
    assert len(cm.paired_notebooks["notebook.ipynb"]) == 2

    # add a cell in the py file
    with open(tmp_py, "a") as fp:
        fp.write("# %%\n2+2\n")

    nb2 = (await ensure_async(cm.get(path="notebook.ipynb")))["content"]
    assert len(nb2.cells) == 1
    assert nb2.cells[0].source == "2+2"


async def test_save_in_auto_extension_global_with_format(
    ipynb_py_R_jl_file, cm, tmpdir
):
    # load notebook
    nb = jupytext.read(ipynb_py_R_jl_file)

    auto_ext = auto_ext_from_metadata(nb.metadata)
    tmp_ipynb = "notebook.ipynb"
    tmp_script = "notebook" + auto_ext

    # create contents manager with default load format as percent
    cm.formats = "ipynb,auto:percent"
    cm.root_dir = str(tmpdir)

    # save notebook
    await ensure_async(cm.save(model=notebook_model(nb), path=tmp_ipynb))

    # check that text representation exists, and is in percent format
    with open(str(tmpdir.join(tmp_script))) as stream:
        assert read_format_from_metadata(stream.read(), auto_ext) == "percent"

    # reload and compare with original notebook
    model = await ensure_async(cm.get(path=tmp_script))

    # saving should not create a format entry #95
    assert "formats" not in model["content"].metadata.get("jupytext", {})

    compare_notebooks(model["content"], nb)


async def test_save_in_auto_extension_local(ipynb_py_R_jl_file, cm, tmpdir):
    # load notebook
    nb = jupytext.read(ipynb_py_R_jl_file)
    nb.metadata.setdefault("jupytext", {})["formats"] = "ipynb,auto:percent"

    auto_ext = auto_ext_from_metadata(nb.metadata)
    tmp_ipynb = "notebook.ipynb"
    tmp_script = "notebook" + auto_ext

    # create contents manager with default load format as percent
    cm.root_dir = str(tmpdir)

    # save notebook
    await ensure_async(cm.save(model=notebook_model(nb), path=tmp_ipynb))

    # check that text representation exists, and is in percent format
    with open(str(tmpdir.join(tmp_script))) as stream:
        assert read_format_from_metadata(stream.read(), auto_ext) == "percent"

    # reload and compare with original notebook
    model = await ensure_async(cm.get(path=tmp_script))

    compare_notebooks(model["content"], nb)


async def test_save_in_pct_and_lgt_auto_extensions(ipynb_py_R_jl_file, cm, tmpdir):
    # load notebook
    nb = jupytext.read(ipynb_py_R_jl_file)

    auto_ext = auto_ext_from_metadata(nb.metadata)
    tmp_ipynb = "notebook.ipynb"
    tmp_pct_script = "notebook.pct" + auto_ext
    tmp_lgt_script = "notebook.lgt" + auto_ext

    # create contents manager with default load format as percent
    cm.formats = "ipynb,.pct.auto,.lgt.auto"
    cm.preferred_jupytext_formats_save = ".pct.auto:percent,.lgt.auto:light"
    cm.root_dir = str(tmpdir)

    # save notebook
    await ensure_async(cm.save(model=notebook_model(nb), path=tmp_ipynb))

    # check that text representation exists in percent format
    with open(str(tmpdir.join(tmp_pct_script))) as stream:
        assert read_format_from_metadata(stream.read(), auto_ext) == "percent"

    # check that text representation exists in light format
    with open(str(tmpdir.join(tmp_lgt_script))) as stream:
        assert read_format_from_metadata(stream.read(), auto_ext) == "light"


async def test_metadata_filter_is_effective(ipynb_py_R_jl_file, cm, tmpdir):
    if re.match(r".*(magic|305).*", ipynb_py_R_jl_file):
        pytest.skip()
    nb = jupytext.read(ipynb_py_R_jl_file)
    tmp_ipynb = "notebook.ipynb"
    tmp_script = "notebook.py"

    # create contents manager
    cm.root_dir = str(tmpdir)

    # save notebook to tmpdir
    await ensure_async(cm.save(model=notebook_model(nb), path=tmp_ipynb))

    # set config
    cm.formats = "ipynb,py"
    cm.notebook_metadata_filter = "jupytext,-all"
    cm.cell_metadata_filter = "-all"

    # load notebook
    nb = (await ensure_async(cm.get(tmp_ipynb)))["content"]

    assert nb.metadata["jupytext"]["cell_metadata_filter"] == "-all"
    assert nb.metadata["jupytext"]["notebook_metadata_filter"] == "jupytext,-all"

    # save notebook again
    await ensure_async(cm.save(model=notebook_model(nb), path=tmp_ipynb))

    # read text version
    nb2 = jupytext.read(str(tmpdir.join(tmp_script)))

    # test no metadata
    assert set(nb2.metadata.keys()) <= {"jupytext", "kernelspec"}
    for cell in nb2.cells:
        assert not cell.metadata

    # read paired notebook
    nb3 = (await ensure_async(cm.get(tmp_script)))["content"]

    compare_notebooks(nb3, nb)


async def test_no_metadata_added_to_scripts_139(tmpdir, cm):
    tmp_script = str(tmpdir.join("script.py"))
    text = """import os


print('hello1')



print('hello2')
"""

    with open(tmp_script, "w") as fp:
        fp.write(text)

    # create contents manager
    cm.root_dir = str(tmpdir)

    # Andre's config #139
    cm.freeze_metadata = True
    cm.notebook_metadata_filter = "-all"
    cm.cell_metadata_filter = "-lines_to_next_cell"

    # load notebook
    model = await ensure_async(cm.get("script.py"))

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
    await ensure_async(cm.save(model=model, path="script.py"))

    with open(tmp_script) as fp:
        compare(fp.read(), text)


@pytest.mark.parametrize("ext", [".py", ".ipynb"])
async def test_local_format_can_deactivate_pairing(ipynb_py_file, cm, ext, tmpdir):
    """This is a test for #157: local format can be used to deactivate the global pairing"""
    nb = jupytext.read(ipynb_py_file)
    nb.metadata["jupytext_formats"] = ext[1:]  # py or ipynb

    # create contents manager with default pairing
    cm.formats = "ipynb,py"
    cm.root_dir = str(tmpdir)

    # save notebook
    await ensure_async(cm.save(model=notebook_model(nb), path="notebook" + ext))

    # check that only the text representation exists
    assert os.path.isfile(str(tmpdir.join("notebook.py"))) == (ext == ".py")
    assert os.path.isfile(str(tmpdir.join("notebook.ipynb"))) == (ext == ".ipynb")
    nb2 = (await ensure_async(cm.get("notebook" + ext)))["content"]
    compare_notebooks(nb2, nb)

    # resave, check again
    await ensure_async(cm.save(model=notebook_model(nb2), path="notebook" + ext))

    assert os.path.isfile(str(tmpdir.join("notebook.py"))) == (ext == ".py")
    assert os.path.isfile(str(tmpdir.join("notebook.ipynb"))) == (ext == ".ipynb")
    nb3 = (await ensure_async(cm.get("notebook" + ext)))["content"]
    compare_notebooks(nb3, nb)


async def test_global_pairing_allows_to_save_other_file_types(rmd_file, cm, tmpdir):
    """This is a another test for #157: local format can be used to deactivate the global pairing"""
    nb = jupytext.read(rmd_file)

    # create contents manager with default pairing
    cm.formats = "ipynb,py"
    cm.root_dir = str(tmpdir)

    # save notebook
    await ensure_async(cm.save(model=notebook_model(nb), path="notebook.Rmd"))

    # check that only the original file is saved
    assert os.path.isfile(str(tmpdir.join("notebook.Rmd")))
    assert not os.path.isfile(str(tmpdir.join("notebook.py")))
    assert not os.path.isfile(str(tmpdir.join("notebook.ipynb")))

    nb2 = (await ensure_async(cm.get("notebook.Rmd")))["content"]
    compare_notebooks(nb2, nb)


@pytest.mark.requires_user_kernel_python3
async def test_python_kernel_preserves_R_files(r_file, cm, tmpdir):
    """Opening a R file with a Jupyter server that has no R kernel should not modify the file"""
    tmp_r_file = str(tmpdir.join("script.R"))
    with open(r_file) as fp:
        script = fp.read()
    with open(tmp_r_file, "w") as fp:
        fp.write(script)

    # create contents manager
    cm.root_dir = str(tmpdir)

    # open notebook, set Python kernel and save
    model = await ensure_async(cm.get("script.R"))
    model["content"].metadata["kernelspec"] = kernelspec_from_language("python")
    await ensure_async(cm.save(model=model, path="script.R"))

    with open(tmp_r_file) as fp:
        script2 = fp.read()

    compare(script2, script)


async def test_pair_notebook_in_another_folder(tmpdir, cm):
    cm.root_dir = str(tmpdir)

    os.makedirs(str(tmpdir.join("notebooks")))
    tmp_ipynb = str(tmpdir.join("notebooks/notebook_name.ipynb"))
    tmp_py = str(tmpdir.join("scripts/notebook_name.py"))

    await ensure_async(
        cm.save(
            model=notebook_model(
                new_notebook(
                    metadata={"jupytext": {"formats": "notebooks//ipynb,scripts//py"}}
                ),
            ),
            path="notebooks/notebook_name.ipynb",
        )
    )

    assert os.path.isfile(tmp_ipynb)
    assert os.path.isfile(tmp_py)

    await ensure_async(cm.get("notebooks/notebook_name.ipynb"))
    await ensure_async(cm.get("scripts/notebook_name.py"))


async def test_pair_notebook_in_dotdot_folder(tmpdir, cm):
    cm.root_dir = str(tmpdir)

    os.makedirs(str(tmpdir.join("notebooks")))
    tmp_ipynb = str(tmpdir.join("notebooks/notebook_name.ipynb"))
    tmp_py = str(tmpdir.join("scripts/notebook_name.py"))

    await ensure_async(
        cm.save(
            model=notebook_model(
                new_notebook(metadata={"jupytext": {"formats": "ipynb,../scripts//py"}})
            ),
            path="notebooks/notebook_name.ipynb",
        )
    )

    assert os.path.isfile(tmp_ipynb)
    assert os.path.isfile(tmp_py)

    await ensure_async(cm.get("notebooks/notebook_name.ipynb"))
    await ensure_async(cm.get("scripts/notebook_name.py"))


async def test_split_at_heading_option(tmpdir, cm):
    text = """Markdown text

# Header one

## Header two
"""
    tmp_md = str(tmpdir.join("notebook.md"))
    with open(tmp_md, "w") as fp:
        fp.write(text)

    cm.root_dir = str(tmpdir)
    cm.split_at_heading = True

    nb = (await ensure_async(cm.get("notebook.md")))["content"]

    # Was rst to md conversion effective?
    assert nb.cells[0].source == "Markdown text"
    assert nb.cells[1].source == "# Header one"
    assert nb.cells[2].source == "## Header two"

    nb.metadata["jupytext"]["notebook_metadata_filter"] = "-all"
    text2 = writes(nb, "md")
    compare(text2, text)


async def test_load_then_change_formats(tmpdir, cm):
    tmp_ipynb = str(tmpdir.join("nb.ipynb"))
    tmp_py = str(tmpdir.join("nb.py"))
    nb = new_notebook(metadata={"jupytext": {"formats": "ipynb,py:light"}})
    write(nb, tmp_ipynb)

    cm.root_dir = str(tmpdir)

    model = await ensure_async(cm.get("nb.ipynb"))
    assert model["content"].metadata["jupytext"]["formats"] == "ipynb,py:light"

    await ensure_async(cm.save(model, path="nb.ipynb"))
    assert os.path.isfile(tmp_py)
    assert read(tmp_py).metadata["jupytext"]["formats"] == "ipynb,py:light"

    time.sleep(0.5)
    del model["content"].metadata["jupytext"]["formats"]
    await ensure_async(cm.save(model, path="nb.ipynb"))
    # test that we have not kept the 'ipynb/py' pairing info, and that we can read the ipynb
    await ensure_async(cm.get("nb.ipynb"))
    os.remove(tmp_py)

    model["content"].metadata.setdefault("jupytext", {})["formats"] = "ipynb,py:percent"
    await ensure_async(cm.save(model, path="nb.ipynb"))
    assert os.path.isfile(tmp_py)
    assert read(tmp_py).metadata["jupytext"]["formats"] == "ipynb,py:percent"
    os.remove(tmp_py)

    del model["content"].metadata["jupytext"]["formats"]
    await ensure_async(cm.save(model, path="nb.ipynb"))
    assert not os.path.isfile(tmp_py)


async def test_set_then_change_formats(tmpdir, cm):
    tmp_py = str(tmpdir.join("nb.py"))
    nb = new_notebook(metadata={"jupytext": {"formats": "ipynb,py:light"}})

    cm.root_dir = str(tmpdir)

    await ensure_async(cm.save(model=notebook_model(nb), path="nb.ipynb"))
    assert os.path.isfile(tmp_py)
    assert read(tmp_py).metadata["jupytext"]["formats"] == "ipynb,py:light"
    os.remove(tmp_py)

    nb.metadata["jupytext"]["formats"] = "ipynb,py:percent"
    await ensure_async(cm.save(model=notebook_model(nb), path="nb.ipynb"))
    assert os.path.isfile(tmp_py)
    assert read(tmp_py).metadata["jupytext"]["formats"] == "ipynb,py:percent"
    os.remove(tmp_py)

    del nb.metadata["jupytext"]["formats"]
    await ensure_async(cm.save(model=notebook_model(nb), path="nb.ipynb"))
    assert not os.path.isfile(tmp_py)


async def test_set_then_change_auto_formats(tmpdir, cm, python_notebook):
    tmp_ipynb = str(tmpdir.join("nb.ipynb"))
    tmp_py = str(tmpdir.join("nb.py"))
    tmp_rmd = str(tmpdir.join("nb.Rmd"))
    nb = new_notebook(metadata=python_notebook.metadata)

    cm.root_dir = str(tmpdir)

    # Pair ipynb/py and save
    nb.metadata["jupytext"] = {"formats": "ipynb,auto:light"}
    await ensure_async(cm.save(model=notebook_model(nb), path="nb.ipynb"))
    assert "nb.py" in cm.paired_notebooks
    assert "nb.auto" not in cm.paired_notebooks
    assert os.path.isfile(tmp_py)
    assert read(tmp_ipynb).metadata["jupytext"]["formats"] == "ipynb,py:light"

    # Pair ipynb/Rmd and save
    time.sleep(0.5)
    nb.metadata["jupytext"] = {"formats": "ipynb,Rmd"}
    await ensure_async(cm.save(model=notebook_model(nb), path="nb.ipynb"))
    assert "nb.Rmd" in cm.paired_notebooks
    assert "nb.py" not in cm.paired_notebooks
    assert "nb.auto" not in cm.paired_notebooks
    assert os.path.isfile(tmp_rmd)
    assert read(tmp_ipynb).metadata["jupytext"]["formats"] == "ipynb,Rmd"
    await ensure_async(cm.get("nb.ipynb"))

    # Unpair and save
    time.sleep(0.5)
    del nb.metadata["jupytext"]
    await ensure_async(cm.save(model=notebook_model(nb), path="nb.ipynb"))
    assert "nb.Rmd" not in cm.paired_notebooks
    assert "nb.py" not in cm.paired_notebooks
    assert "nb.auto" not in cm.paired_notebooks
    await ensure_async(cm.get("nb.ipynb"))


async def test_share_py_recreate_ipynb(tmpdir, cm, ipynb_py_R_jl_file):
    tmp_ipynb = str(tmpdir.join("nb.ipynb"))
    tmp_py = str(tmpdir.join("nb.py"))

    cm.root_dir = str(tmpdir)

    # set default py format
    cm.preferred_jupytext_formats_save = "py:percent"

    # every new file is paired
    cm.formats = "ipynb,py"

    # the text files don't need a YAML header
    cm.notebook_metadata_filter = "-all"
    cm.cell_metadata_filter = "-all"

    nb = read(ipynb_py_R_jl_file)
    model_ipynb = await ensure_async(cm.save(model=notebook_model(nb), path="nb.ipynb"))

    assert os.path.isfile(tmp_ipynb)
    assert os.path.isfile(tmp_py)

    os.remove(tmp_ipynb)

    # reopen and save nb.py
    model = await ensure_async(cm.get("nb.py"))
    await ensure_async(cm.save(model=model, path="nb.py"))

    # ipynb is re-created
    assert os.path.isfile(tmp_ipynb)

    # save time of ipynb is that of py file
    assert model_ipynb["last_modified"] == model["last_modified"]


async def test_vim_folding_markers(tmpdir, cm):
    tmp_ipynb = str(tmpdir.join("nb.ipynb"))
    tmp_py = str(tmpdir.join("nb.py"))

    cm.root_dir = str(tmpdir)

    # Default Vim folding markers
    cm.cell_markers = "{{{,}}}"
    cm.formats = "ipynb,py:light"

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
    await ensure_async(cm.save(model=notebook_model(nb), path="nb.ipynb"))

    assert os.path.isfile(tmp_ipynb)
    assert os.path.isfile(tmp_py)

    nb2 = (await ensure_async(cm.get("nb.ipynb")))["content"]
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


async def test_vscode_pycharm_folding_markers(tmpdir, cm):
    tmp_ipynb = str(tmpdir.join("nb.ipynb"))
    tmp_py = str(tmpdir.join("nb.py"))

    cm.root_dir = str(tmpdir)

    # Default VScode/PyCharm folding markers
    cm.cell_markers = "region,endregion"
    cm.formats = "ipynb,py:light"

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
    await ensure_async(cm.save(model=notebook_model(nb), path="nb.ipynb"))

    assert os.path.isfile(tmp_ipynb)
    assert os.path.isfile(tmp_py)

    nb2 = (await ensure_async(cm.get("nb.ipynb")))["content"]
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


async def test_open_file_with_cell_markers(tmpdir, cm):
    tmp_py = str(tmpdir.join("nb.py"))

    cm.root_dir = str(tmpdir)

    # Default VScode/PyCharm folding markers
    cm.cell_markers = "region,endregion"

    text = """# +
# this is a unique code cell
1 + 1

2 + 2
"""

    with open(tmp_py, "w") as fp:
        fp.write(text)

    nb = (await ensure_async(cm.get("nb.py")))["content"]
    assert len(nb.cells) == 1

    await ensure_async(cm.save(model=notebook_model(nb), path="nb.py"))

    with open(tmp_py) as fp:
        text2 = fp.read()

    expected = """# region
# this is a unique code cell
1 + 1

2 + 2
# endregion
"""

    compare(text2, expected)


async def test_save_file_with_cell_markers(tmpdir, cm):
    tmp_py = str(tmpdir.join("nb.py"))

    cm.root_dir = str(tmpdir)

    # Default VScode/PyCharm folding markers
    cm.cell_markers = "region,endregion"

    text = """# +
# this is a unique code cell
1 + 1

2 + 2
"""

    with open(tmp_py, "w") as fp:
        fp.write(text)

    nb = (await ensure_async(cm.get("nb.py")))["content"]
    assert len(nb.cells) == 1

    await ensure_async(cm.save(model=notebook_model(nb), path="nb.py"))

    with open(tmp_py) as fp:
        text2 = fp.read()

    compare(
        text2,
        """# region
# this is a unique code cell
1 + 1

2 + 2
# endregion
""",
    )

    nb2 = (await ensure_async(cm.get("nb.py")))["content"]
    compare_notebooks(nb2, nb)
    assert nb2.metadata["jupytext"]["cell_markers"] == "region,endregion"


async def test_notebook_extensions(tmpdir, cm, cwd_tmpdir):
    nb = new_notebook()
    write(nb, "script.py")
    write(nb, "notebook.Rmd")
    write(nb, "notebook.ipynb")

    cm.root_dir = str(tmpdir)
    cm.notebook_extensions = "ipynb,Rmd"

    model = await ensure_async(cm.get("notebook.ipynb"))
    assert model["type"] == "notebook"

    model = await ensure_async(cm.get("notebook.Rmd"))
    assert model["type"] == "notebook"

    model = await ensure_async(cm.get("script.py"))
    assert model["type"] == "file"


async def test_notebook_extensions_in_config(tmpdir, cm, cwd_tmpdir):
    nb = new_notebook()
    write(nb, "script.py")
    write(nb, "notebook.Rmd")
    write(nb, "notebook.ipynb")
    tmpdir.join("jupytext.toml").write("""notebook_extensions = ["ipynb", "Rmd"]""")

    cm.root_dir = str(tmpdir)

    model = await ensure_async(cm.get("notebook.ipynb"))
    assert model["type"] == "notebook"

    model = await ensure_async(cm.get("notebook.Rmd"))
    assert model["type"] == "notebook"

    model = await ensure_async(cm.get("script.py"))
    assert model["type"] == "file"


async def test_invalid_config_in_cm(tmpdir, cm, cwd_tmpdir):
    nb = new_notebook()
    write(nb, "notebook.ipynb")
    tmpdir.join("pyproject.toml").write(
        """[tool.jupysql.SqlMagic]
autopandas = False
displaylimit = 1"""
    )

    cm.root_dir = str(tmpdir)

    # list directory
    await ensure_async(cm.get(""))

    model = await ensure_async(cm.get("notebook.ipynb"))
    assert model["type"] == "notebook"


async def test_download_file_318(tmpdir, cm):
    tmp_ipynb = str(tmpdir.join("notebook.ipynb"))
    tmp_py = str(tmpdir.join("notebook.py"))

    nb = new_notebook()
    nb.metadata["jupytext"] = {"formats": "ipynb,py"}
    write(nb, tmp_ipynb)
    write(nb, tmp_py)

    cm.root_dir = str(tmpdir)
    cm.notebook_extensions = "ipynb"

    model = await ensure_async(
        cm.get("notebook.ipynb", content=True, type=None, format=None)
    )
    assert model["type"] == "notebook"


async def test_markdown_and_r_extensions(tmpdir, cm):
    tmp_r = str(tmpdir.join("script.r"))
    tmp_markdown = str(tmpdir.join("notebook.markdown"))

    nb = new_notebook()
    write(nb, tmp_r)
    write(nb, tmp_markdown)

    cm.root_dir = str(tmpdir)

    model = await ensure_async(cm.get("script.r"))
    assert model["type"] == "notebook"

    model = await ensure_async(cm.get("notebook.markdown"))
    assert model["type"] == "notebook"


async def test_server_extension_issubclass(cm):
    class SubClassTextFileContentsManager(jupytext.TextFileContentsManager):
        pass

    assert not isinstance(
        SubClassTextFileContentsManager, jupytext.TextFileContentsManager
    )
    assert issubclass(SubClassTextFileContentsManager, jupytext.TextFileContentsManager)


async def test_multiple_pairing(tmpdir, cm):
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

    cm.root_dir = str(tmpdir)

    await ensure_async(
        cm.save(model=notebook_model(nb("saved from cm")), path="notebook.ipynb")
    )
    compare_notebooks(jupytext.read(tmp_ipynb), nb("saved from cm"))
    compare_notebooks(jupytext.read(tmp_md), nb("saved from cm"))
    compare_notebooks(jupytext.read(tmp_py), nb("saved from cm"))

    jupytext.write(nb("md edited"), tmp_md)
    model = await ensure_async(cm.get("notebook.ipynb"))
    compare_notebooks(model["content"], nb("md edited"))

    await ensure_async(cm.save(model=model, path="notebook.ipynb"))
    compare_notebooks(jupytext.read(tmp_ipynb), nb("md edited"))
    compare_notebooks(jupytext.read(tmp_md), nb("md edited"))
    compare_notebooks(jupytext.read(tmp_py), nb("md edited"))

    jupytext.write(nb("py edited"), tmp_py)

    # Loading the md file give the content of that file
    model = await ensure_async(cm.get("notebook.md"))
    compare_notebooks(model["content"], nb("md edited"))

    # Loading the ipynb files gives the content of the most recent text file
    model = await ensure_async(cm.get("notebook.ipynb"))
    compare_notebooks(model["content"], nb("py edited"))

    await ensure_async(cm.save(model=model, path="notebook.ipynb"))
    compare_notebooks(jupytext.read(tmp_ipynb), nb("py edited"))
    compare_notebooks(jupytext.read(tmp_md), nb("py edited"))
    compare_notebooks(jupytext.read(tmp_py), nb("py edited"))

    model_ipynb = await ensure_async(
        cm.get("notebook.ipynb", content=False, load_alternative_format=False)
    )
    model_md = await ensure_async(
        cm.get("notebook.md", content=False, load_alternative_format=False)
    )
    model_py = await ensure_async(
        cm.get("notebook.py", content=False, load_alternative_format=False)
    )

    # ipynb is the oldest one, then py, then md
    # so that we read cell inputs from the py file
    assert model_ipynb["last_modified"] <= model_py["last_modified"]
    assert model_py["last_modified"] <= model_md["last_modified"]


async def test_filter_jupytext_version_information_416(
    python_notebook, cm, tmpdir, cwd_tmpdir
):
    cm.root_dir = str(tmpdir)
    cm.notebook_metadata_filter = "-jupytext.text_representation.jupytext_version"

    # load notebook
    notebook = python_notebook
    notebook.metadata["jupytext_formats"] = "ipynb,py"
    model = notebook_model(notebook)

    # save to ipynb and py
    await ensure_async(cm.save(model=model, path="notebook.ipynb"))

    assert os.path.isfile("notebook.py")

    # read py file
    with open("notebook.py") as fp:
        text = fp.read()

    assert "---" in text
    assert "jupytext:" in text
    assert "kernelspec:" in text
    assert "jupytext_version:" not in text


@pytest.mark.requires_myst
async def test_new_untitled(tmpdir, cm):
    cm.root_dir = str(tmpdir)

    # untitled is "Untitled" only when the locale is English #636
    untitled, ext = (await ensure_async(cm.new_untitled(type="notebook")))[
        "path"
    ].split(".")
    assert untitled
    assert ext == "ipynb"

    # Jupytext related files
    assert (await ensure_async(cm.new_untitled(type="notebook", ext=".md")))[
        "path"
    ] == untitled + "1.md"
    assert (await ensure_async(cm.new_untitled(type="notebook", ext=".py")))[
        "path"
    ] == untitled + "2.py"
    assert (await ensure_async(cm.new_untitled(type="notebook", ext=".md:myst")))[
        "path"
    ] == untitled + "3.md"
    assert (await ensure_async(cm.new_untitled(type="notebook", ext=".py:percent")))[
        "path"
    ] == untitled + "4.py"
    assert (await ensure_async(cm.new_untitled(type="notebook", ext=".Rmd")))[
        "path"
    ] == untitled + "5.Rmd"

    # Test native formats that should not be changed by Jupytext and model should
    # not contain any Jupytext metadata neither file name should start with Uppercase
    for ext in [".py", ".md"]:
        model = await ensure_async(cm.new_untitled(type="file", ext=ext))
        assert model["content"] is None
        assert model["path"] == f"untitled{ext}"
    assert (await ensure_async(cm.new_untitled(type="directory")))[
        "path"
    ] == "Untitled Folder"


async def test_nested_prefix(tmpdir, cm):
    cm.root_dir = str(tmpdir)

    # save to ipynb and py
    nb = new_notebook(
        cells=[new_code_cell("1+1"), new_markdown_cell("Some text")],
        metadata={"jupytext": {"formats": "ipynb,nested/prefix//.py"}},
    )
    await ensure_async(cm.save(model=notebook_model(nb), path="notebook.ipynb"))

    assert tmpdir.join("nested").join("prefix").join("notebook.py").isfile()


async def test_timestamp_is_correct_after_reload_978(tmp_path, cm, python_notebook):
    """Here we reproduce the conditions in Issue #978 and make sure no
    warning is generated"""
    nb = python_notebook
    nb.metadata["jupytext"] = {"formats": "ipynb,py:percent"}

    cm.root_dir = str(tmp_path)

    ipynb_py_R_jl_file = tmp_path / "nb.ipynb"
    py_file = tmp_path / "nb.py"

    # 1. Save the paired notebook
    await ensure_async(cm.save(notebook_model(nb), path="nb.ipynb"))
    assert ipynb_py_R_jl_file.exists()
    assert py_file.exists()

    # and reload to get the original timestamp
    org_model = await ensure_async(cm.get("nb.ipynb"))

    # 2. Edit the py file
    time.sleep(0.5)
    text = py_file.read_text()
    text = (
        text
        + """

# %%
# A new cell
2 + 2
"""
    )

    py_file.write_text(text)

    # 3. Reload the paired notebook and make sure it has the modified content
    model = await ensure_async(cm.get("nb.ipynb"))
    nb = model["content"]
    assert "A new cell" in nb.cells[-1].source
    assert model["last_modified"] > org_model["last_modified"]


async def test_move_paired_notebook_to_subdir_1059(tmp_path, cm, python_notebook):
    (tmp_path / "jupytext.toml").write_text(
        'formats = "notebooks///ipynb,scripts///py:percent"\n'
    )
    cm.root_dir = str(tmp_path)

    # create paired notebook
    (tmp_path / "notebooks").mkdir()
    await ensure_async(
        cm.save(notebook_model(python_notebook), path="notebooks/my_notebook.ipynb")
    )
    assert (tmp_path / "notebooks" / "my_notebook.ipynb").exists()
    assert (tmp_path / "scripts" / "my_notebook.py").exists()

    # move notebook
    (tmp_path / "notebooks" / "subdir").mkdir()
    await ensure_async(
        cm.rename_file(
            "notebooks/my_notebook.ipynb", "notebooks/subdir/my_notebook.ipynb"
        )
    )
    assert (tmp_path / "notebooks" / "subdir" / "my_notebook.ipynb").exists()
    assert (tmp_path / "scripts" / "subdir" / "my_notebook.py").exists()

    assert not (tmp_path / "notebooks" / "my_notebook.ipynb").exists()
    assert not (tmp_path / "scripts" / "my_notebook.py").exists()

    # check notebook content
    model = await ensure_async(cm.get("scripts/subdir/my_notebook.py"))
    nb = model["content"]
    compare_notebooks(nb, python_notebook, fmt="py:percent")


async def test_hash_changes_if_paired_file_is_edited(tmp_path, cm, python_notebook):
    # 1. write py ipynb

    if "require_hash" not in inspect.signature(cm.get).parameters:
        pytest.skip(
            reason="This JupytextContentsManager does not have a 'require_hash' parameter in cm.get"
        )

    cm.formats = "ipynb,py:percent"
    cm.root_dir = str(tmp_path)

    # save ipynb
    nb = python_notebook
    nb_name = "notebook.ipynb"
    await ensure_async(cm.save(model=notebook_model(nb), path=nb_name))
    org_model = await ensure_async(cm.get(nb_name, require_hash=True))

    py_file = tmp_path / "notebook.py"

    text = py_file.read_text()
    assert "# %% [markdown]" in text.splitlines(), text

    # modify the timestamp of the paired file
    time.sleep(0.5)
    py_file.write_text(text)
    model = await ensure_async(cm.get(nb_name, require_hash=True))
    # not sure why the hash changes on Windows?
    assert (model["hash"] == org_model["hash"]) or (os.name == "nt")

    # modify the paired file
    py_file.write_text(text + "\n# %%\n1 + 1\n")

    new_model = await ensure_async(cm.get(nb_name, require_hash=True))
    assert new_model["hash"] != org_model["hash"]

    # the hash is for the pair (inputs first)
    model_from_py_file = await ensure_async(cm.get("notebook.py", require_hash=True))
    assert model_from_py_file["hash"] == new_model["hash"]


@pytest.mark.requires_myst
async def test_metadata_stays_in_order_1368(
    tmp_path,
    cm,
    md="""---
jupytext:
  formats: md:myst
  notebook_metadata_filter: -jupytext.text_representation.jupytext_version
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
kernelspec:
  display_name: itables
  language: python
  name: itables
---

A markdown cell
""",
):
    cm.root_dir = str(tmp_path)

    (tmp_path / "nb.md").write_text(md)

    model = await ensure_async(cm.get(path="nb.md"))
    assert list(model["content"]["metadata"].keys()) == [
        "jupytext",
        "kernelspec",
    ], "order must be preserved"

    cm.save(model=model, path="nb.md")
    compare((tmp_path / "nb.md").read_text(), md)


@pytest.mark.requires_myst
async def test_jupytext_orders_root_metadata(
    tmp_path,
    cm,
    md="""---
title: Quick test
jupytext:
  formats: md:myst
  notebook_metadata_filter: -jupytext.text_representation.jupytext_version
  root_level_metadata_filter: -title
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
kernelspec:
  display_name: itables
  language: python
  name: itables
---

A markdown cell
""",
):
    cm.root_dir = str(tmp_path)

    (tmp_path / "nb.md").write_text(md)

    model = await ensure_async(cm.get(path="nb.md"))
    assert list(model["content"]["metadata"].keys()) == [
        "jupytext",
        "kernelspec",
    ], "order must be preserved"

    # simulate jupyter changing the order of the metadata
    model["content"]["metadata"]["jupytext"] = model["content"]["metadata"].pop(
        "jupytext"
    )
    assert list(model["content"]["metadata"].keys()) == ["kernelspec", "jupytext"]

    cm.save(model=model, path="nb.md")
    compare((tmp_path / "nb.md").read_text(), md)
