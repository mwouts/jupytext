# In this notebook, we benchmark the Jupytext formats for Jupyter notebooks against the base format
# Open this script as a notebook in Jupyter to run it and see the plots

import time
import copy
import pandas as pd
import plotly.graph_objects as go
from plotly.colors import DEFAULT_PLOTLY_COLORS

import nbformat
import jupytext

# The notebook to be tested
notebook = jupytext.read('World population.ipynb')

# Same notebook, with no outputs, for a fair comparison
notebook_no_outputs = copy.deepcopy(notebook)
for cell in notebook_no_outputs.cells:
    cell.outputs = []
    cell.execution_count = None

# +
JUPYTEXT_FORMATS = ['ipynb', 'md', 'py:light', 'py:percent', 'py:sphinx']

# Let's see if we have pandoc here
try:
    jupytext.writes(notebook, fmt='md:pandoc')
    JUPYTEXT_FORMATS.append('md:pandoc')
except jupytext.formats.JupytextFormatError as err:
    print(str(err))


# Let's see if we have myst-parser installed here
try:
    jupytext.writes(notebook, fmt='myst')
    JUPYTEXT_FORMATS.append('myst')
except jupytext.formats.JupytextFormatError as err:
    print(str(err))

# -


def sample_perf(nb, n=30):
    samples = pd.DataFrame(
        pd.np.NaN,
        index=pd.MultiIndex.from_product(
            (range(n), ['nbformat'] + JUPYTEXT_FORMATS), names=['sample', 'implementation']),
        columns=pd.Index(['size', 'read', 'write'], name='measure'))

    for i, fmt in samples.index:
        t0 = time.time()
        if fmt == 'nbformat':
            text = nbformat.writes(nb)
        else:
            text = jupytext.writes(nb, fmt)
        t1 = time.time()
        samples.loc[(i, fmt), 'write'] = t1 - t0
        samples.loc[(i, fmt), 'size'] = len(text)
        t0 = time.time()
        if fmt == 'nbformat':
            nbformat.reads(text, as_version=4)
        else:
            jupytext.reads(text, fmt)
        t1 = time.time()
        samples.loc[(i, fmt), 'read'] = t1 - t0
    return samples


def performance_plot(perf, title):
    formats = ['nbformat'] + JUPYTEXT_FORMATS
    mean = perf.groupby('implementation').mean().loc[formats]
    std = perf.groupby('implementation').std().loc[formats]
    data = [go.Bar(x=mean.index,
                   y=mean[col],
                   error_y=dict(
                       type='data',
                       array=std[col],
                       color=color,
                       thickness=0.5
                   ) if col != 'size' else dict(),
                   name=col,
                   yaxis={'read': 'y1', 'write': 'y2', 'size': 'y3'}[col])
            for col, color in zip(mean.columns, DEFAULT_PLOTLY_COLORS)]
    layout = go.Layout(title=title,
                       xaxis=dict(title='Implementation', anchor='y3'),
                       yaxis=dict(domain=[0.7, 1], title='Read (secs)'),
                       yaxis2=dict(domain=[0.35, .65], title='Write (secs)'),
                       yaxis3=dict(domain=[0, .3], title='Size')
                       )
    return go.Figure(data=data, layout=layout)


perf_no_outputs = sample_perf(notebook_no_outputs, 30)

performance_plot(perf_no_outputs, 'Benchmarking Jupytext on the World Population notebook<br>(Outputs filtered)')

perf = sample_perf(notebook, 30)

performance_plot(perf, 'Benchmarking Jupytext on the World Population notebook<br>(With outputs)')
