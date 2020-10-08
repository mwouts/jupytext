"""Read and write Jupyter notebooks as text files"""

from .jupytext import read, write, writes, reads
from .formats import NOTEBOOK_EXTENSIONS, guess_format, get_format_implementation
from .reraise import reraise
from .version import __version__

try:
    from .contentsmanager import build_jupytext_contents_manager_class
except ImportError as err:
    build_jupytext_contents_manager = reraise(err)

try:
    from .contentsmanager import TextFileContentsManager
except ImportError as err:
    TextFileContentsManager = reraise(err)


def load_jupyter_server_extension(app):  # pragma: no cover
    """Use Jupytext's contents manager"""
    if hasattr(app.contents_manager_class, "default_jupytext_formats"):
        app.log.info(
            "[Jupytext Server Extension] NotebookApp.contents_manager_class is "
            "(a subclass of) jupytext.TextFileContentsManager already - OK"
        )
        return

    # The server extension call is too late!
    # The contents manager was set at NotebookApp.init_configurables

    # Let's change the contents manager class
    app.log.info(
        "[Jupytext Server Extension] Deriving a JupytextContentsManager "
        "from {}".format(app.contents_manager_class.__name__)
    )
    app.contents_manager_class = build_jupytext_contents_manager_class(
        app.contents_manager_class
    )

    try:
        # And rerun selected init steps from https://github.com/jupyter/notebook/blob/
        # 132f27306522b32fa667a6b208034cb7a04025c9/notebook/notebookapp.py#L1634-L1638

        # app.init_configurables()
        app.contents_manager = app.contents_manager_class(parent=app, log=app.log)
        app.session_manager.contents_manager = app.contents_manager

        # app.init_components()
        # app.init_webapp()
        app.web_app.settings["contents_manager"] = app.contents_manager

        # app.init_terminals()
        # app.init_signal()

    except Exception:
        app.log.error(
            """[Jupytext Server Extension] An error occurred. Please deactivate the server extension with
    jupyter serverextension disable jupytext
and configure the contents manager manually by adding
    c.NotebookApp.contents_manager_class = "jupytext.TextFileContentsManager"
to your .jupyter/jupyter_notebook_config.py file.
"""
        )
        raise


def _jupyter_nbextension_paths():  # pragma: no cover
    """Allows commands like
    jupyter nbextension install --py jupytext
    jupyter nbextension enable --py jupytext
    jupyter labextension install jupyterlab-jupytext"""
    return [
        dict(
            section="notebook",
            # the path is relative to the `jupytext` directory
            src="nbextension",
            # directory in the `nbextension/` namespace
            dest="jupytext",
            # _also_ in the `nbextension/` namespace
            require="jupytext/index",
        )
    ]


__all__ = [
    "read",
    "write",
    "writes",
    "reads",
    "NOTEBOOK_EXTENSIONS",
    "guess_format",
    "get_format_implementation",
    "TextFileContentsManager",
    "__version__",
]
