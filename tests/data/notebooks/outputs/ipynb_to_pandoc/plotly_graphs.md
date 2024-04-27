---
jupyter:
  kernelspec:
    display_name: Python 3
    language: python
    name: python3
  nbformat: 4
  nbformat_minor: 2
---

::: {.cell .markdown}
This notebook contains complex outputs, including plotly javascript graphs.
:::

::: {.cell .markdown}
# Interactive plots
:::

::: {.cell .markdown}
We use Plotly\'s connected mode to make the notebook lighter - when connected, the notebook downloads the `plotly.js` library from the web.
:::

::: {#cell-1 .cell .code}
``` python
import plotly.offline as offline
offline.init_notebook_mode(connected=True)
```
:::

::: {#cell-2 .cell .code}
``` python
import plotly.graph_objects as go
fig = go.Figure(
    data=[go.Bar(y=[2, 3, 1])],
    layout=go.Layout(title="bar plot"))
fig.show()
fig.data[0].marker = dict(color='purple')
fig
```
:::
