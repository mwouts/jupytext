import copy
import os
import time

import pytest
from nbformat.v4.nbbase import new_code_cell, new_markdown_cell, new_notebook, new_output

import jupytext

pytest.importorskip("jupyter_server_ydoc", reason="requires jupyter-collaboration")
from jupyter_server_ydoc.loaders import FileLoader  # noqa: E402
from jupyter_server_ydoc.rooms import DocumentRoom  # noqa: E402

pytestmark = pytest.mark.asyncio


class _FileIdManager:
    def __init__(self, path):
        self.path = path

    def get_path(self, file_id):
        return self.path


class _EventLogger:
    def emit(self, *args, **kwargs):
        pass


async def _load_with_jupyter_collaboration(contents_manager, path):
    file_id = f"test-file-id:{path}"
    loader = FileLoader(
        file_id=file_id,
        file_id_manager=_FileIdManager(path),
        contents_manager=contents_manager,
        log=contents_manager.log,
    )
    room = DocumentRoom(
        room_id=f"test-room:{path}",
        file_format="json",
        file_type="notebook",
        file=loader,
        logger=_EventLogger(),
        ystore=None,
        log=contents_manager.log,
        save_delay=None,
    )
    try:
        await room.initialize()
        if hasattr(room._document, "aget"):
            return await room._document.aget()
        return room._document.get()
    finally:
        await room.stop()


async def test_jupyter_collaboration_loads_text_notebook(tmpdir, cm):
    cm.root_dir = str(tmpdir)

    nb = new_notebook(
        metadata={
            "jupytext": {"formats": "py:percent"},
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
        },
        cells=[new_markdown_cell("A text notebook"), new_code_cell("1 + 1")],
    )
    jupytext.write(nb, str(tmpdir.join("text_notebook.py")), fmt="py:percent")

    content = await _load_with_jupyter_collaboration(cm, "text_notebook.py")

    assert [cell["cell_type"] for cell in content["cells"]] == ["markdown", "code"]
    assert [cell["source"] for cell in content["cells"]] == ["A text notebook", "1 + 1"]
    assert content["metadata"]["jupytext"]["formats"] == "py:percent"


async def test_jupyter_collaboration_loads_paired_notebook(tmpdir, cm):
    cm.root_dir = str(tmpdir)

    nb = new_notebook(
        metadata={
            "jupytext": {"formats": "ipynb,py:percent"},
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
        },
        cells=[
            new_code_cell(
                "1 + 1",
                execution_count=1,
                outputs=[
                    new_output(
                        "execute_result",
                        data={"text/plain": "2"},
                        execution_count=1,
                    )
                ],
            )
        ],
    )
    jupytext.write(nb, str(tmpdir.join("paired.ipynb")))

    # Make the text representation newer and with updated inputs. Jupytext should
    # combine those inputs with the outputs from the paired ipynb file when the
    # notebook is loaded through Jupyter Collaboration's DocumentRoom.
    text_nb = copy.deepcopy(nb)
    text_nb.cells[0].source = "1 + 2"
    jupytext.write(text_nb, str(tmpdir.join("paired.py")), fmt="py:percent")
    timestamp = time.time()
    os.utime(str(tmpdir.join("paired.ipynb")), (timestamp, timestamp))
    os.utime(str(tmpdir.join("paired.py")), (timestamp + 2, timestamp + 2))

    content = await _load_with_jupyter_collaboration(cm, "paired.ipynb")

    assert content["metadata"]["jupytext"]["formats"] == "ipynb,py:percent"
    assert content["cells"][0]["source"] == "1 + 2"
    assert content["cells"][0]["outputs"][0]["data"] == {"text/plain": "2"}
    assert content["cells"][0]["execution_count"] == 1
