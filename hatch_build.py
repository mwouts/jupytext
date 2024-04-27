import logging
import os
import sys

from hatch_jupyter_builder.plugin import JupyterBuildHook

LOGGER = logging.getLogger(__name__)


class CustomBuildHook(JupyterBuildHook):
    """
    We use a custom build hook to detect pre-commit environments. In those
    environments there is no need to build the extension (and, in addition
    the build will fail if npm is not available, which is often the case
    of pre-commit environments).
    """

    def initialize(self, version, _):
        if "/.cache/pre-commit/".replace("/", os.path.sep) in sys.executable:
            LOGGER.info(
                "This environment looks like a pre-commit environment. "
                "We will skip the build of the Jupytext extension for JupyterLab."
            )
            self._skipped = True
            return

        return super().initialize(version=version, _=_)


# hatch wants a single hook
del JupyterBuildHook
