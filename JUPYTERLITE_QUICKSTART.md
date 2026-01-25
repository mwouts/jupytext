# Jupytext for JupyterLite - Quick Start Guide

Get Jupytext running in JupyterLite in 5 minutes!

## What is This?

This enables [Jupytext](https://github.com/mwouts/jupytext) to work in [JupyterLite](https://jupyterlite.readthedocs.io/) - a version of Jupyter that runs entirely in your browser with no server. Perfect for:

- 📚 **Teaching**: Share interactive notebooks via simple URLs
- 🌐 **Static sites**: Deploy Jupyter on GitHub Pages, Netlify, etc.
- 🔒 **Offline work**: Run Jupyter without internet (after first load)
- 🚀 **Easy sharing**: No server setup required

## Quick Start

### Option 1: Try the Demo (2 minutes)

**Using Pixi (Recommended):**

```bash
# Clone the repository
git clone https://github.com/mwouts/jupytext.git
cd jupytext

# Build and serve with pixi
pixi run -e jupyterlite build-jupyterlite
pixi run -e jupyterlite serve-jupyterlite
```

**Without Pixi:**

```bash
cd jupytext/demo/jupyterlite-example
pip install -r requirements.txt
./build.sh
jupyter lite serve
```

Open http://localhost:8000 and try opening `welcome.py` as a notebook!

### Option 2: Deploy Your Own Site (5 minutes)

1. **Create project structure**:
   ```bash
   mkdir my-jupyterlite-site
   cd my-jupyterlite-site
   mkdir notebooks
   ```

2. **Create `requirements.txt`**:
   ```
   jupytext[jupyterlite]
   ```

3. **Create `jupyter-lite.json`**:
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

4. **Add a notebook** (`notebooks/demo.py`):
   ```python
   # %% [markdown]
   # # Hello JupyterLite + Jupytext!

   # %%
   import sys
   print(f"Python {sys.version}")
   print("Running in your browser! 🎉")
   ```

5. **Build and serve**:
   ```bash
   pip install jupytext[jupyterlite]
   jupyter lite build --contents notebooks/
   jupyter lite serve
   ```

6. **Deploy**:
   - Upload `_output/` to any static host
   - Or use GitHub Pages (see [deployment guide](docs/jupyterlite.md#deploying-jupyterlite-with-jupytext))

## Supported Formats

All Jupytext formats work:

| Format | Extension | Example |
|--------|-----------|---------|
| Python | `.py` | `notebook.py` |
| R | `.R` | `analysis.R` |
| Julia | `.jl` | `simulation.jl` |
| Markdown | `.md` | `document.md` |
| R Markdown | `.Rmd` | `report.Rmd` |
| Quarto | `.qmd` | `article.qmd` |

## How to Use

1. **Open text files as notebooks**: Right-click any `.py`, `.md`, etc. → "Open With" → "Notebook"

2. **Save notebooks as text**: File → Save As → `notebook.py`

3. **Edit either format**: Changes sync automatically!

## Real-World Example: GitHub Pages

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy JupyterLite

on:
  push:
    branches: [main]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pages: write
      id-token: write
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install jupytext[jupyterlite]
      - run: jupyter lite build --contents notebooks/
      - uses: actions/upload-pages-artifact@v3
        with:
          path: ./_output
      - uses: actions/deploy-pages@v4
```

Push to GitHub, enable Pages, and your site is live! 🚀

## Key Differences from Regular Jupyter

| Feature | Regular Jupyter | JupyterLite + Jupytext |
|---------|----------------|------------------------|
| Server | ✅ Required | ❌ Not needed |
| Installation | Complex | Simple (static files) |
| Hosting | Dynamic server | Static files anywhere |
| Paired notebooks | ✅ Auto-sync | ⚠️ Manual only |
| Pre-commit hooks | ✅ Supported | ❌ Not supported |
| First load | Fast | Slower (~10-30s for Pyodide) |
| Subsequent loads | Fast | Fast (cached) |
| Offline use | After setup | After first load |

## Performance

- **First load**: 10-30 seconds (downloads Pyodide + Jupytext)
- **Cached loads**: ~1 second
- **Conversion**: < 1 second for typical notebooks
- **Memory**: ~200MB browser memory needed

## Troubleshooting

### "Pyodide not available"
- Use a modern browser (Chrome, Firefox, Safari)
- Check WebAssembly is enabled
- Try a hard refresh (Ctrl+Shift+R)

### Files don't open as notebooks
- Add `# %%` markers for Python files
- Check file extension is supported
- Look in browser console for errors

### Slow loading
- First load always takes longer (downloads Pyodide)
- Subsequent loads use browser cache
- Consider using a CDN for better performance

## Documentation

- 📖 **Full guide**: [docs/jupyterlite.md](docs/jupyterlite.md)
- 🔧 **Implementation details**: [JUPYTERLITE_IMPLEMENTATION.md](JUPYTERLITE_IMPLEMENTATION.md)
- 💡 **Example project**: [demo/jupyterlite-example/](demo/jupyterlite-example/)
- 📦 **Extension source**: [jupyterlab/packages/jupyterlite-jupytext/](jupyterlab/packages/jupyterlite-jupytext/)

## Live Examples

- [Jupytext Demo Site](https://jupytext.github.io/demo) - Coming soon!
- [JupyterLite Documentation](https://jupyterlite.readthedocs.io/en/latest/try/lab)

## Contributing

Found a bug or want to contribute? See [CONTRIBUTING.md](CONTRIBUTING.md)!

## License

MIT License - Same as Jupytext

---

**Questions?** Open an [issue](https://github.com/mwouts/jupytext/issues) or check the [documentation](https://jupytext.readthedocs.io/)!
