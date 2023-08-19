"""
helper to inspect / initialize jupyterlab labconfig settings
that are required to open jupytext notebooks in jupyterlab by default
when these settings are not present, a double click on a jupytext
notebook will cause jupyterlab to open it in an editor, i.e. as a text file
"""

import copy
import json
import logging
import pprint
from pathlib import Path


class LabConfig:
    SETTINGS = Path.home() / ".jupyter" / "labconfig" / "default_setting_overrides.json"

    LANGUAGES = [
        "python",
        "markdown",
        "myst",
        "r-markdown",
        "quarto",
        "julia",
        "r",
    ]

    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.config = {}
        # the state before any changes
        self._prior_config = {}

    def read(self):
        """
        read the labconfig settings file
        """
        try:
            if self.SETTINGS.exists():
                with self.SETTINGS.open() as fid:
                    self.config = json.load(fid)
        except OSError as exc:
            self.logger.error(f"Could not read {self.SETTINGS}", exc)
            return False
        # store for further comparison
        self._prior_config = copy.deepcopy(self.config)
        return self

    def list(self):
        """
        list the current labconfig settings
        """
        self.logger.debug(
            f"Current @jupyterlab/docmanager-extension:plugin in {self.SETTINGS}"
        )
        docmanager = self.config.get("@jupyterlab/docmanager-extension:plugin", {})
        for key, value in docmanager.items():
            print(f"{key}:")
            pprint.pprint(value)

    def set_default_viewers(self, languages=None):
        if not languages:
            languages = self.LANGUAGES
        for language in languages:
            self.set_default_viewer(language)
        return self

    def set_default_viewer(self, language):
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
        if language not in viewers:
            viewers[language] = "Jupytext Notebook"

    def write(self) -> bool:
        """
        write the labconfig settings file
        """
        # compare - avoid changing the file if nothing changed
        if self.config == self._prior_config:
            self.logger.info(f"Nothing to do for {self.SETTINGS}")
            return True

        # save
        try:
            self.SETTINGS.parent.mkdir(parents=True, exist_ok=True)
            with self.SETTINGS.open("w") as fid:
                json.dump(self.config, fid, indent=2)
            # useful in case of successive write's
            self._prior_config = copy.deepcopy(self.config)
            return True
        except OSError as exc:
            self.logger.error(f"Could not write {self.SETTINGS}", exc)
            return False
