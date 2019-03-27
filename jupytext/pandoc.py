"""Jupyter notebook to Markdown and back, using Pandoc"""

import subprocess
import packaging.version
import nbformat


class PandocError(ChildProcessError):
    """An error related to Pandoc"""
    pass


def pandoc(args, text=''):
    """Execute pandoc with the given arguments"""
    cmd = [u'pandoc'] + args.split()
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    out, err = proc.communicate(text.encode('utf-8'))
    if proc.returncode:
        raise PandocError('pandoc exited with return code {}\n{}'.format(proc.returncode, str(err)))
    return out.decode('utf-8')


def pandoc_version():
    """Pandoc's version number"""
    version = pandoc(u'--version').splitlines()[0].split()[1]

    if packaging.version.parse(version) < packaging.version.parse('2.7.1'):
        raise PandocError('Please install pandoc>=2.7.1 (found version {})'.format(version))

    return version


def md_to_notebook(text):
    """Convert a Markdown text to a Jupyter notebook, using Pandoc"""
    json = pandoc(u'--from markdown --to ipynb', text)
    return nbformat.reads(json, as_version=4)


def notebook_to_md(notebook):
    """Convert a notebook to its Markdown representation, using Pandoc"""
    text = nbformat.writes(notebook)
    return pandoc(u'--from ipynb --to markdown', text)
