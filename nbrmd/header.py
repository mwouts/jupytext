import re
import yaml
from nbformat.v4.nbbase import new_raw_cell

_header_re = re.compile(r"^---\s*$")
_empty_re = re.compile(r"^\s*$")
_jupyter_re = re.compile(r"^jupyter\s*:\s*$")
_leftspace_re = re.compile(r"^\s")


def metadata_and_cell_to_header(nb, prefix=''):
    '''
    Return the text header corresponding to a notebook, and remove the
    first cell of the notebook if it contained the header
    '''

    header = []
    skipline = True

    if len(nb.cells):
        c = nb.cells[0]
        if c.cell_type == 'raw':
            lines = c.source.strip('\n\t ').splitlines()
            if len(lines) >= 2 \
                    and _header_re.match(lines[0]) \
                    and _header_re.match(lines[-1]):
                header = lines[1:-1]
                skipline = not c.metadata.get('noskipline', False)
                nb.cells = nb.cells[1:]

    metadata = nb.get('metadata', {})
    if len(metadata):
        header.extend(yaml.safe_dump({'jupyter': metadata},
                                     default_flow_style=False).splitlines())

    if len(header):
        header = ['---'] + header + ['---']

    if len(prefix):
        header = [prefix + h for h in header]

    if skipline:
        header += ['']

    return header


def header_to_metadata_and_cell(lines, prefix=''):
    '''
    Return the metadata, first cell of notebook, and next loc in text
    '''

    header = []
    jupyter = []
    injupyter = False
    ended = False

    for i, l in enumerate(lines):
        if not l.startswith(prefix):
            break

        l = l[len(prefix):]

        if i == 0:
            if _header_re.match(l):
                continue
            else:
                break

        if i > 0 and _header_re.match(l):
            ended = True
            break

        if _jupyter_re.match(l):
            injupyter = True
        elif not _leftspace_re.match(l):
            injupyter = False

        if injupyter:
            jupyter.append(l)
        else:
            header.append(l)

    if ended:
        metadata = {}
        if len(jupyter):
            print('\n'.join(jupyter))
            metadata = yaml.load('\n'.join(jupyter))['jupyter']

        skipline = True
        if len(lines) > i + 1:
            l = lines[i + 1]
            if not _empty_re.match(l):
                skipline = False
            else:
                i = i + 1
        else:
            skipline = False

        if len(header):
            cell = new_raw_cell(source='\n'.join(['---'] + header + ['---']),
                                metadata={} if skipline else
                                {'noskipline': True})
        else:
            cell = None

        return metadata, cell, i + 1

    return {}, None, 0
