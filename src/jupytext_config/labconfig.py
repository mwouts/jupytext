"""
helper to inspect / initialize jupyterlab labconfig settings
that are required to open jupytext notebooks in jupyterlab by default
when these settings are not present, a double click on a jupytext
notebook will cause jupyterlab to open it in an editor, i.e. as a text file
"""

import json
import logging
from pathlib import Path


class LabConfig:
    DOCTYPES = [
        "python",
        "markdown",
        "myst",
        "r-markdown",
        "quarto",
        "julia",
        "r",
    ]

    def __init__(self, *, settings_file, logger=None):
        self.settings_file = Path(settings_file)
        self.logger = logger or logging.getLogger(__name__)
        self.config = {}

    def read(self):
        """
        read the labconfig settings file
        """
        if self.settings_file.exists():
            with self.settings_file.open() as fid:
                self.config = json.load(fid)
        else:
            self.logger.info(f"Could not read from {self.settings_file} (not found)")

        return self

    def get_viewers(self):
        return self.config.setdefault(
            "@jupyterlab/docmanager-extension:plugin", {}
        ).setdefault("defaultViewers", {})

    def list_default_viewer(self):
        """
        list the current labconfig settings
        """
        self.logger.debug(
            f"Current @jupyterlab/docmanager-extension:plugin in {self.settings_file}"
        )
        for key, value in self.get_viewers().items():
            print(f"{key}: {value}")

    def set_default_viewers(self, doctypes=None):
        if not doctypes:
            doctypes = self.DOCTYPES
        for doctype in doctypes:
            self.set_default_viewer(doctype)
        return self

    def set_default_viewer(self, doctype):
        viewers = self.get_viewers()
        if doctype not in viewers:
            viewers[doctype] = "Jupytext Notebook"

    def unset_default_viewers(self, doctypes=None):
        if not doctypes:
            doctypes = self.DOCTYPES
        for doctype in doctypes:
            self.unset_default_viewer(doctype)
        return self

    def unset_default_viewer(self, doctype):
        viewers = self.get_viewers()
        if doctype in viewers:
            del viewers[doctype]

    def write(self):
        """
        write the labconfig settings file
        """
        self.settings_file.parent.mkdir(parents=True, exist_ok=True)
        with self.settings_file.open("w") as fid:
            json.dump(self.config, fid, indent=2)
