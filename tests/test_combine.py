from nbformat.v4.nbbase import new_code_cell, new_markdown_cell, new_notebook
from jupytext.combine import combine_inputs_with_outputs
import jupytext


def test_combine():
    nb_source = new_notebook(
        cells=[new_markdown_cell('Markdown text'),
               new_code_cell('a=3'),
               new_code_cell('a+1'),
               new_code_cell('a+1'),
               new_markdown_cell('Markdown text'),
               new_code_cell('a+2')])

    nb_outputs = new_notebook(
        cells=[new_markdown_cell('Markdown text'),
               new_code_cell('a=3'),
               new_code_cell('a+1'),
               new_code_cell('a+2'),
               new_markdown_cell('Markdown text')])

    nb_outputs.cells[2].outputs = ['4']
    nb_outputs.cells[3].outputs = ['5']

    combine_inputs_with_outputs(nb_source, nb_outputs)

    assert nb_source.cells[2].outputs == ['4']
    assert nb_source.cells[3].outputs == []
    assert nb_source.cells[5].outputs == ['5']


def test_read_text_and_combine_with_outputs(tmpdir):
    tmp_ipynb = 'notebook.ipynb'
    tmp_script = 'notebook.py'

    with(open(str(tmpdir.join(tmp_script)), 'w')) as fp:
        fp.write("""# ---
# jupyter:
#   jupytext_formats: ipynb,py:light
# ---

1+1

2+2

3+3
""")

    with(open(str(tmpdir.join(tmp_ipynb)), 'w')) as fp:
        fp.write("""{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 1,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "2"
      ]
     },
     "execution_count": 1,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "1+1"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "6"
      ]
     },
     "execution_count": 3,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "3+3"
   ]
  }
 ],
 "metadata": {},
 "nbformat": 4,
 "nbformat_minor": 2
}
""")

    # create contents manager
    cm = jupytext.TextFileContentsManager()
    cm.root_dir = str(tmpdir)

    # load notebook from script
    model = cm.get(tmp_script)
    nb = model['content']

    assert nb.cells[0]['source'] == '1+1'
    assert nb.cells[1]['source'] == '2+2'
    assert nb.cells[2]['source'] == '3+3'

    # No output for the second cell, which is not in the ipynb
    assert nb.cells[0]['outputs']
    assert not nb.cells[1]['outputs']
    assert nb.cells[2]['outputs']

    assert len(nb.cells) == 3
