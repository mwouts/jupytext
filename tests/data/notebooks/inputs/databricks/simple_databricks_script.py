# Databricks notebook source
# MAGIC %md
# MAGIC This is an example notebook

# COMMAND ----------

# MAGIC %pip install plotly

# COMMAND ----------

import plotly.graph_objs as go

data = go.Bar(x=['A', 'B', 'C'], y=[10, 20, 15])
go.Figure(data=[data])

# COMMAND ----------
