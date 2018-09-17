"""Text notebook exporters for nbconvert"""

from traitlets import default
from nbconvert.exporters import Exporter
from .formats import get_format
from .jupytext import writes


class TextNotebookExporter(Exporter):
    """Export to the desired format"""

    fmt = None

    @default('file_extension')
    def _file_extension_default(self):
        return self.fmt.extension

    def from_notebook_node(self, nb, resources=None, **kw):
        resources = resources or {}
        resources['output_extension'] = self.file_extension
        return writes(nb,
                      ext=self.fmt.extension,
                      format_name=self.fmt.format_name), resources


class RMarkdownExporter(TextNotebookExporter):
    """RMarkdown exporter for nbconvert"""
    fmt = get_format('.Rmd')


class MarkdownExporter(TextNotebookExporter):
    """Markdown exporter for nbconvert"""
    fmt = get_format('.md')


class LightPythonExporter(TextNotebookExporter):
    """Light python exporter for nbconvert"""
    fmt = get_format('.py', 'light')


class LightJuliaExporter(TextNotebookExporter):
    """Light Julia exporter for nbconvert"""
    fmt = get_format('.jl', 'light')


class RKnitrSpinExporter(TextNotebookExporter):
    """R knitr::spin exporter for nbconvert"""
    fmt = get_format('.R', 'rscript')
