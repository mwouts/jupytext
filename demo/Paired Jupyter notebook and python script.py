# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.3'
#       jupytext_version: 1.0.0-dev
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# This is a notebook that you can use to experiment with the jupytext package.
#
# Proposed experimentations are
# 1. Open this Jupyter notebook (extension .ipynb) in Jupyter
# 2. Open the corresponding '.py' file. That is, copy the url for the notebook, that looks like
# ```
# https://hub.mybinder.org/user/mwouts-jupytext-g7315gce/notebooks/demo/Sample%20notebook%20with%20python%20representation.ipynb
# ```
# replace `/notebooks/` with `/edit/`, and change the extension from `ipynb` to `py`, to get an url like
# ```
# https://hub.mybinder.org/user/mwouts-jupytext-g7315gce/edit/demo/Sample%20notebook%20with%20python%20representation.py
# ```
# 3. Modify the notebook in Jupyter. Save. Refresh the python file in the editor, and observe the changes.
# 4. Now, modify the python file, save, and refresh the Jupyter notebook. Observe how inputs were updated, outputs preserved when possible, and kernel was left unchanged.
# 5. Browse the github repo using Jupyter in binder, and open arbitrary python files as notebooks. Run them when applicable.

# %matplotlib inline

# +
import matplotlib.pyplot as plt
import numpy as np

t = np.arange(0.0, 2.0, 0.01)
s = 1 + np.sin(2*np.pi*t)
plt.plot(t, s)

plt.xlabel('time (s)')
plt.ylabel('voltage (mV)')
plt.title('About as simple as it gets, folks')
# -

plt.show()


