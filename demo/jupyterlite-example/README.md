# Example JupyterLite Configuration with Jupytext

This directory contains a minimal JupyterLite configuration with Jupytext enabled.

> **Note**: The JupyterLite extension is included in the main Jupytext package as an optional extra.
> Install with `pip install jupytext[jupyterlite]` or use the local source with `-e ../../[jupyterlite]`.

## Structure

```
.
├── jupyter-lite.json       # JupyterLite configuration
├── requirements.txt        # Python dependencies for building
├── notebooks/              # Your notebook files (.py, .md, .ipynb, etc.)
└── README.md              # This file
```

## Quick Start

### Using Pixi (Recommended)

```bash
# From the repository root
cd ../..

# Build the JupyterLite site (installs deps, builds extension, builds site)
pixi run -e jupyterlite build-jupyterlite

# Serve the site
pixi run -e jupyterlite serve-jupyterlite
```

### Using the Build Script (Alternative)

```bash
# Enter pixi shell first
pixi shell -e jupyterlite

# Run the build script (builds extension + site)
./build.sh

# Serve the site
jupyter lite serve
```

### Without Pixi

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Build the local Jupytext extension**:
   ```bash
   cd ../../jupyterlab/packages/jupyterlite-jupytext
   jlpm install
   jlpm build
   cd -
   ```

3. **Add your notebooks**:
   - Place `.py`, `.md`, `.R`, or `.ipynb` files in the `notebooks/` directory
   - You can use subdirectories for organization

4. **Build the site**:
   ```bash
   jupyter lite build
   ```

5. **Preview locally**:
   ```bash
   jupyter lite serve
   ```
   Then open http://localhost:8000 in your browser

6. **Deploy**:
   - Copy the `_output/` directory to your web server
   - Or use the provided GitHub Actions workflow for automatic deployment

## Example Notebooks

### Python Script (analysis.py)

```python
# %% [markdown]
# # Data Analysis Example
# 
# This notebook demonstrates using Jupytext with JupyterLite.

# %%
import sys
print(f"Python version: {sys.version}")
print("Running in your browser via Pyodide!")

# %% [markdown]
# ## Load Some Data

# %%
data = [1, 2, 3, 4, 5]
sum_data = sum(data)
print(f"Sum: {sum_data}")

# %% [markdown]
# ## Visualize
# 
# Note: For plotting in JupyterLite, use matplotlib which is available in Pyodide

# %%
# Uncomment when matplotlib is loaded:
# import matplotlib.pyplot as plt
# plt.plot(data)
# plt.title("Simple Plot")
# plt.show()
```

### Markdown Document (tutorial.md)

```markdown
---
jupyter:
  kernelspec:
    display_name: Python 3
    language: python
    name: python3
---

# Tutorial

This is a markdown-based notebook.

```python
print("Hello from a markdown notebook!")
```

## Benefits

- Easy to read and edit in any text editor
- Great for version control
- Perfect for documentation with code
```

## Configuration Options

### jupyter-lite.json

```json
{
  "jupyter-lite-schema-version": 0,
  "jupyter-config-data": {
    "litePluginSettings": {
      "@jupyterlite/jupytext-extension": {
        "enabled": true,
        "defaultFormat": "py:percent"
      }
    }
  }
}
```

### Customizing File Types

To enable specific file types to be opened as notebooks, Jupytext automatically recognizes:
- `.py` - Python scripts
- `.r`, `.R` - R scripts
- `.jl` - Julia scripts
- `.md` - Markdown files
- `.Rmd` - R Markdown
- `.qmd` - Quarto

## Deployment Options

### Option 1: GitHub Pages

Use the provided `.github/workflows/deploy.yml` to automatically build and deploy on push.

### Option 2: Netlify

Add a `netlify.toml`:

```toml
[build]
  command = "pip install -r requirements.txt && jupyter lite build"
  publish = "_output"

[[plugins]]
  package = "@netlify/plugin-python"
```

### Option 3: Vercel

Add a `vercel.json`:

```json
{
  "buildCommand": "pip install -r requirements.txt && jupyter lite build",
  "outputDirectory": "_output"
}
```

### Option 4: Static Server

Simply upload the `_output/` directory to any static file host.

## Tips

1. **Keep notebooks small**: Browser memory is limited
2. **Use lazy loading**: Don't load all notebooks at once
3. **Optimize images**: Compress images to reduce download time
4. **Test locally**: Always test with `jupyter lite serve` before deploying

## Troubleshooting

### Jupytext not working

- Clear browser cache
- Check browser console for errors
- Verify requirements.txt includes `jupyterlite-jupytext`

### Slow loading

- First load always takes longer (downloads Pyodide)
- Subsequent loads use browser cache
- Consider using a CDN for assets

### Files not opening as notebooks

- Check file has correct extension
- For Python files, ensure they have `# %%` markers
- Check file syntax is valid

## Learn More

- [JupyterLite documentation](https://jupyterlite.readthedocs.io/)
- [Jupytext documentation](https://jupytext.readthedocs.io/)
- [Jupytext with JupyterLite guide](../docs/jupyterlite.md)
