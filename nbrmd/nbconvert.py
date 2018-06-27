import nbrmd
from traitlets import default
from nbconvert.exporters import Exporter


class RMarkdownExporter(Exporter):
    """
    Exports to a R markdown document (.Rmd)
    """

    @default('file_extension')
    def _file_extension_default(self):
        return '.Rmd'

    def from_notebook_node(self, nb, resources=None, **kw):
        resources = resources or {}
        resources['output_extension'] = self.file_extension
        return nbrmd.writes(nb), resources
