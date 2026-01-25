# %% [markdown]
# # Welcome to Jupytext + JupyterLite!
# 
# This notebook demonstrates Jupytext running entirely in your browser thanks to JupyterLite and Pyodide.
#
# ## What's happening here?
#
# 1. This `.py` file is being displayed as a Jupyter notebook
# 2. All conversion happens in your browser (no server needed!)
# 3. You can edit and run code just like in regular Jupyter

# %%
import sys
print(f"Python version: {sys.version}")
print(f"Platform: {sys.platform}")
print("\n✨ You're running Python in WebAssembly!")

# %% [markdown]
# ## Try Some Code
#
# Feel free to modify and run the cells below:

# %%
# Simple calculation
numbers = [1, 2, 3, 4, 5]
total = sum(numbers)
average = total / len(numbers)

print(f"Numbers: {numbers}")
print(f"Sum: {total}")
print(f"Average: {average}")

# %% [markdown]
# ## Why This Is Cool
#
# - **No server required**: Everything runs in your browser
# - **Version control friendly**: This notebook is just a plain Python file
# - **Easy sharing**: Deploy as a static website
# - **Offline capable**: Works without internet after first load
# - **Git-friendly**: Meaningful diffs, no cell IDs or execution counts

# %% [markdown]
# ## Jupytext Formats
#
# This notebook uses the "percent" format with `# %%` cell markers.
# Jupytext supports many formats:
#
# - **Python**: `py:percent`, `py:light`, `py:nomarker`
# - **Markdown**: `md`, `Rmd`, `qmd`, `myst`
# - **R**: `r:percent`, `r:light`
# - **Julia**: `jl:percent`, `jl:light`
# - And more!

# %%
# You can even use Jupytext metadata
# (Check the file header in a text editor)

formats = ["py:percent", "md", "Rmd", "qmd"]
print("Supported formats:")
for fmt in formats:
    print(f"  - {fmt}")

# %% [markdown]
# ## Learn More
#
# - [Jupytext Documentation](https://jupytext.readthedocs.io/)
# - [JupyterLite Documentation](https://jupyterlite.readthedocs.io/)
# - [GitHub Repository](https://github.com/mwouts/jupytext)
#
# ---
#
# **Try it yourself**: Click "File → Save As..." and save this notebook as a different format!
