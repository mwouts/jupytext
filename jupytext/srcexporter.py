"""
R and Py notebook exporters for nbconvert
"""

from traitlets import default
from nbconvert.exporters import Exporter
import jupytext


class PyNotebookExporter(Exporter):
    """
    Exports to a python notebook (.py)
    """

    @default('file_extension')
    def _file_extension_default(self):
        return '.py'

    def from_notebook_node(self, nb, resources=None, **kw):
        resources = resources or {}
        resources['output_extension'] = self.file_extension
        return jupytext.writes(nb, ext='.py'), resources


class JlNotebookExporter(Exporter):
    """
    Exports to a julia notebook (.jl)
    """

    @default('file_extension')
    def _file_extension_default(self):
        return '.jl'

    def from_notebook_node(self, nb, resources=None, **kw):
        resources = resources or {}
        resources['output_extension'] = self.file_extension
        return jupytext.writes(nb, ext='.jl'), resources


class RNotebookExporter(Exporter):
    """
    Exports to a R notebook (.R)
    """

    @default('file_extension')
    def _file_extension_default(self):
        return '.R'

    def from_notebook_node(self, nb, resources=None, **kw):
        resources = resources or {}
        resources['output_extension'] = self.file_extension
        return jupytext.writes(nb, ext='.R'), resources
