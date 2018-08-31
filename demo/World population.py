# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
#   language_info:
#     codemirror_mode:
#       name: ipython
#       version: 3
#     file_extension: .py
#     mimetype: text/x-python
#     name: python
#     nbconvert_exporter: python
#     pygments_lexer: ipython3
#     version: 3.6.6
#   nbrmd_format_version: '1.1'
#   nbrmd_formats: ipynb,py,md
# ---

# # A quick insight at world population
#
# In the below we retrieve population data from the [World Bank](http://www.worldbank.org/)
# using the [wbdata](https://github.com/OliverSherouse/wbdata) python package

# + {}
import pandas as pd
import wbdata as wb

pd.options.display.max_rows = 6
# -

# We found the adequate indicator using search method - or the World Bank site.

wb.search_indicators('Population, total')  # SP.POP.TOTL
# wb.search_indicators('area') # https://data.worldbank.org/indicator is easier to use

# Now we download the population data
indicators = {'SP.POP.TOTL': 'Population, total',
              'AG.SRF.TOTL.K2': 'Surface area (sq. km)',
              'AG.LND.TOTL.K2': 'Land area (sq. km)',
              'AG.LND.ARBL.ZS': 'Arable land (% of land area)'}
data = wb.get_dataframe(indicators, convert_date=True)
data

# Country to continent classification
continent = pd.read_csv(
    'https://raw.githubusercontent.com/dbouquin/IS_608/master/NanosatDB_munging/Countries-Continents.csv')
continent = continent.rename(columns=str.lower).set_index('country')
continent

# + {}
# Start plotly
import plotly.offline as offline
import plotly.graph_objs as go

offline.init_notebook_mode()
# -

# Population per continent over time
u = data['Population, total'].unstack()
# Not perfect: incorrect classification removes almost 1B population! Total now at 8B almost.
# Correct classification may come with https://github.com/OliverSherouse/wbdata/issues/22
bars = [go.Bar(x=pop.reset_index().date, y=pop, name=continent) for continent, pop in
        u.groupby(continent.reindex(u.index).continent).sum().stack().groupby('continent')]
fig = go.Figure(data=bars, layout=go.Layout(title='World population',
                                            barmode='stack'))
offline.iplot(fig)
