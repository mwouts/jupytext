"""Jupyter server and lab extension entry points"""

from jupytext.reraise import reraise

try:
    from jupytext.contentsmanager import build_jupytext_contents_manager_class
except ImportError as err:
    build_jupytext_contents_manager = reraise(err)


def load_jupyter_server_extension(app):  # pragma: no cover
    """Use Jupytext's contents manager"""
    if hasattr(app.contents_manager_class, "formats"):
        app.log.info(
            "[Jupytext Server Extension] NotebookApp.contents_manager_class is "
            "(a subclass of) jupytext.TextFileContentsManager already - OK"
        )
        return

    # The server extension call is too late!
    # The contents manager was set at NotebookApp.init_configurables

    # Let's change the contents manager class
    base_class = app.contents_manager_class
    if "async" in base_class.__name__.lower():
        app.log.warning(
            "[Jupytext Server Extension] Async contents managers like {} "
            "are not supported at the moment "
            "(https://github.com/mwouts/jupytext/issues/1020). "
            "We will derive a contents manager from LargeFileManager instead.".format(
                base_class.__name__
            )
        )
        from jupyter_server.services.contents.largefilemanager import (  # noqa
            LargeFileManager,
        )

        base_class = LargeFileManager

    app.log.info(
        "[Jupytext Server Extension] Deriving a JupytextContentsManager "
        "from {}".format(base_class.__name__)
    )
    app.contents_manager_class = build_jupytext_contents_manager_class(base_class)

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


def _jupyter_labextension_paths():
    return [{"src": "labextension", "dest": "jupyterlab-jupytext"}]
