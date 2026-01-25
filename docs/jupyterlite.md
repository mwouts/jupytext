# Using Jupytext with JupyterLite

[JupyterLite](https://jupyterlite.readthedocs.io/) is a distribution of JupyterLab that runs entirely in the browser using WebAssembly. Since JupyterLite doesn't have a traditional server backend, the standard Jupytext server extension cannot be used. Instead, we provide a specialized JupyterLite extension that runs Jupytext entirely in the browser.

## How It Works

The JupyterLite extension uses [Pyodide](https://pyodide.org/) to run Python (and Jupytext) directly in your browser:

1. **Client-side conversion**: When you open a `.py`, `.md`, or `.R` file, Jupytext's Python code runs in the browser to convert it to notebook format
2. **Transparent experience**: The conversion happens automatically - you don't need to do anything special
3. **No server needed**: Everything runs in WebAssembly, making it perfect for static sites and offline use

## Installation

### For JupyterLite Site Maintainers

If you're deploying a JupyterLite site and want to include Jupytext support:

#### Option 1: Using pip

```bash
# Install Jupytext with JupyterLite support
pip install jupytext[jupyterlite]

# Build your JupyterLite site
jupyter lite build --contents your_notebooks/
```

#### Option 2: Including in `jupyter-lite.json`

Add the extension to your JupyterLite configuration:

```json
{
  "jupyter-lite-schema-version": 0,
  "jupyter-config-data": {
    "litePluginSettings": {
      "@jupyterlite/jupytext-extension": {
        "enabled": true
      }
    }
  }
}
```

### For End Users

If you're visiting a JupyterLite site that has Jupytext installed:

1. Simply open any supported text file (`.py`, `.md`, `.R`, etc.)
2. Right-click and choose "Open With → Notebook"
3. The file will automatically be converted and displayed as a notebook!

## Supported Formats

All standard Jupytext formats are supported:

- **Python scripts**: `.py` (percent, light, nomarker)
- **R scripts**: `.R` (percent, light)
- **Julia scripts**: `.jl` (percent, light)
- **Markdown**: `.md`
- **R Markdown**: `.Rmd`
- **Quarto**: `.qmd`
- **MyST Markdown**: `.md` with MyST syntax

## Usage Examples

### Opening a Python Script as a Notebook

1. Create or upload a Python script `analysis.py`:
   ```python
   # %% [markdown]
   # # Data Analysis
   # This notebook analyzes some data

   # %%
   import pandas as pd
   df = pd.read_csv('data.csv')
   df.head()
   ```

2. In JupyterLite, right-click `analysis.py` → "Open With" → "Notebook"
3. The file opens as a fully functional Jupyter notebook!

### Creating a New Text Notebook

1. Create a new notebook in JupyterLite
2. Add some cells with code and markdown
3. Save the notebook as `notebook.py` instead of `notebook.ipynb`
4. The notebook is automatically converted to a Python script with Jupytext formatting

### Version Control Friendly Workflows

Since JupyterLite can be deployed as a static site, you can:

1. Store your notebooks as `.py` files in a Git repository
2. Deploy JupyterLite with Jupytext extension
3. Users can open and edit `.py` files as notebooks in their browser
4. Changes can be downloaded and committed back to Git

This is perfect for:
- Teaching environments
- Documentation sites
- Interactive tutorials
- Collaborative coding workshops

## Performance Considerations

### First Load

The first time Jupytext is used in a session, it needs to:
- Download Pyodide (~30MB, compressed)
- Install Jupytext and its dependencies in the browser
- Initialize the Python environment

This can take 10-30 seconds depending on your connection. However:
- The browser caches everything, so subsequent loads are much faster
- The loading happens in the background - you can browse while it loads

### Conversion Speed

Once loaded, conversion is typically:
- **Small files** (<100 cells): Nearly instantaneous
- **Medium files** (100-500 cells): 1-2 seconds
- **Large files** (>500 cells): 3-10 seconds

These times are comparable to server-side Jupytext on modest hardware.

## Limitations

### Technical Limitations

1. **Browser requirements**: Requires a modern browser with WebAssembly support
2. **Memory usage**: Pyodide requires significant browser memory (~100-200MB)
3. **No paired notebooks**: Automatic pairing (e.g., keeping `.ipynb` and `.py` in sync) is not supported since there's no persistent server
4. **No pre-commit hooks**: Client-side environment doesn't support Git hooks

### Workarounds

For features that require server-side support:
- Use the standard Jupytext server extension in a regular Jupyter environment for development
- Use JupyterLite + Jupytext for distribution and read-only or lightweight editing

## Configuration

### Extension Settings

Configure the extension through JupyterLab Settings Editor:

```json
{
  "enabled": true,
  "defaultFormat": "py:percent",
  "autoConvert": true
}
```

### File-level Configuration

You can still use Jupytext metadata in notebook files:

```python
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
# ---
```

The extension will respect these settings when converting.

## Deploying JupyterLite with Jupytext

### GitHub Pages Example

Here's how to deploy a JupyterLite site with Jupytext on GitHub Pages:

1. Create `requirements.txt`:
   ```
   jupyterlite-core
   jupyterlite-jupytext
   ```

2. Create `.github/workflows/deploy.yml`:
   ```yaml
   name: Deploy JupyterLite

   on:
     push:
       branches: [main]

   jobs:
     build:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3

         - uses: actions/setup-python@v4
           with:
             python-version: '3.11'

         - name: Install dependencies
           run: |
             pip install -r requirements.txt

         - name: Build JupyterLite site
           run: |
             jupyter lite build --contents notebooks/

         - name: Deploy to GitHub Pages
           uses: peaceiris/actions-gh-pages@v3
           with:
             github_token: ${{ secrets.GITHUB_TOKEN }}
             publish_dir: ./_output
   ```

3. Add your Python/Markdown notebooks to the `notebooks/` folder

4. Push to GitHub - your site will be live at `https://username.github.io/repo-name/`

### Static Hosting

For other static hosts (Netlify, Vercel, etc.):

```bash
# Build the site
jupyter lite build --contents notebooks/

# Deploy the _output directory to your host
```

## Troubleshooting

### Extension Not Loading

**Symptom**: Text files don't open as notebooks

**Solutions**:
- Check browser console for errors
- Verify the extension is listed in JupyterLite's extension manager
- Try a hard refresh (Ctrl+Shift+R)

### Pyodide Download Fails

**Symptom**: "Failed to load Pyodide" error

**Solutions**:
- Check internet connection
- Try a different browser
- Check if your network blocks WebAssembly downloads

### Conversion Errors

**Symptom**: File opens as text instead of notebook

**Solutions**:
- Check file format is valid (e.g., valid Python syntax)
- Verify file has Jupytext markers (like `# %%`)
- Check browser console for detailed error messages

## Example Sites

Several sites use JupyterLite with Jupytext:

- [Jupytext Demo Site](https://jupytext.github.io/demo) (coming soon)
- Your site here! Open an issue to be listed

## Comparison: Server vs. Browser

| Feature | Server-side Jupytext | JupyterLite Jupytext |
|---------|---------------------|---------------------|
| Conversion speed | Very fast | Fast (after initial load) |
| Installation | `pip install jupytext` | Include in JupyterLite build |
| Paired notebooks | ✅ Automatic sync | ❌ Not supported |
| Pre-commit hooks | ✅ Supported | ❌ Not supported |
| Offline use | ✅ (after setup) | ✅ (after first load) |
| Server required | ✅ Yes | ❌ No |
| Static hosting | ❌ No | ✅ Yes |
| Easy sharing | Medium | ✅ Very easy |

## Contributing

The JupyterLite extension is part of the main Jupytext repository. To contribute:

1. Fork the [Jupytext repository](https://github.com/mwouts/jupytext)
2. Make changes in `jupyterlab/packages/jupyterlite-jupytext/`
3. Test with JupyterLite
4. Submit a pull request

See our [contributing guide](contributing.md) for details.

## Learn More

- [JupyterLite documentation](https://jupyterlite.readthedocs.io/)
- [Pyodide documentation](https://pyodide.org/)
- [Jupytext documentation](https://jupytext.readthedocs.io/)
- [WebAssembly](https://webassembly.org/)
