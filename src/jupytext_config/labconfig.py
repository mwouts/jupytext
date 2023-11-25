"""
helper to inspect / initialize jupyterlab labconfig settings
that are required to open jupytext notebooks in jupyterlab by default
when these settings are not present, a double click on a jupytext
notebook will cause jupyterlab to open it in an editor, i.e. as a text file
"""

import copy
import json
import logging

# import pprint
from pathlib import Path

DEFAULT_SETTINGS_FILE = (
    Path.home() / ".jupyter" / "labconfig" / "default_setting_overrides.json"
)


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

    def __init__(self, logger=None, settings_file=DEFAULT_SETTINGS_FILE):
        self.logger = logger or logging.getLogger(__name__)
        self.config = {}
        # the state before any changes
        self._prior_config = {}
        self.settings_file = Path(settings_file)

    def read(self):
        """
        read the labconfig settings file
        """
        try:
            if self.settings_file.exists():
                with self.settings_file.open() as fid:
                    self.config = json.load(fid)
        except OSError as exc:
            self.logger.error(f"Could not read {self.settings_file}", exc)
            return False
        # store for further comparison
        self._prior_config = copy.deepcopy(self.config)
        return self

    def list_default_viewer(self):
        """
        list the current labconfig settings
        """
        self.logger.debug(
            f"Current @jupyterlab/docmanager-extension:plugin in {self.settings_file}"
        )
        docmanager = self.config.get("@jupyterlab/docmanager-extension:plugin", {})
        viewers = docmanager.get("defaultViewers", {})
        for key, value in viewers.items():
            print(f"{key}: {value}")

    def set_default_viewers(self, doctypes=None):
        if not doctypes:
            doctypes = self.DOCTYPES
        for doctype in doctypes:
            self.set_default_viewer(doctype)
        return self

    def set_default_viewer(self, doctype):
        if "@jupyterlab/docmanager-extension:plugin" not in self.config:
            self.config["@jupyterlab/docmanager-extension:plugin"] = {}
        if (
            "defaultViewers"
            not in self.config["@jupyterlab/docmanager-extension:plugin"]
        ):
            self.config["@jupyterlab/docmanager-extension:plugin"][
                "defaultViewers"
            ] = {}
        viewers = self.config["@jupyterlab/docmanager-extension:plugin"][
            "defaultViewers"
        ]
        if doctype not in viewers:
            viewers[doctype] = "Jupytext Notebook"

    def unset_default_viewers(self, doctypes=None):
        if not doctypes:
            doctypes = self.DOCTYPES
        for doctype in doctypes:
            self.unset_default_viewer(doctype)
        return self

    def unset_default_viewer(self, doctype):
        viewers = self.config.get("@jupyterlab/docmanager-extension:plugin", {}).get(
            "defaultViewers", {}
        )
        if doctype not in viewers:
            return
        del viewers[doctype]

    def write(self) -> bool:
        """
        write the labconfig settings file
        """
        # compare - avoid changing the file if nothing changed
        if self.config == self._prior_config:
            self.logger.info(f"Nothing to do for {self.settings_file}")
            return True

        # save
        try:
            self.settings_file.parent.mkdir(parents=True, exist_ok=True)
            with self.settings_file.open("w") as fid:
                json.dump(self.config, fid, indent=2)
            # useful in case of successive write's
            self._prior_config = copy.deepcopy(self.config)
            return True
        except OSError as exc:
            self.logger.error(f"Could not write {self.settings_file}", exc)
            return False
