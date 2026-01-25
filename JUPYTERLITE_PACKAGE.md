# JupyterLite Support in Jupytext

## Overview

The JupyterLite extension is now **included in the main Jupytext package** as an optional feature, rather than being distributed as a separate package. This simplifies installation and maintenance.

## Installation

Simply install Jupytext with the `jupyterlite` extra:

```bash
pip install jupytext[jupyterlite]
```

This will:
- Install the core Jupytext package
- Install JupyterLite dependencies
- Make the JupyterLite extension available for use

## Quick Start

```bash
# Install with JupyterLite support
pip install jupytext[jupyterlite]

# Create a site with your notebooks
jupyter lite build --contents notebooks/

# Test locally
jupyter lite serve
```

## What's Included

When you install `jupytext[jupyterlite]`, you get:

1. **Core Jupytext**: All standard Jupytext features
2. **JupyterLite Support**: The browser-based extension
3. **Dependencies**: `jupyterlite-core` and required packages

## Package Structure

```
jupytext/
├── src/jupytext/              # Core Jupytext Python code
├── jupyterlab/
│   ├── packages/
│   │   ├── jupyterlab-jupytext-extension/   # Standard JupyterLab extension
│   │   └── jupyterlite-jupytext/            # JupyterLite extension (NEW)
│   └── jupyterlab_jupytext/   # Server extension
└── pyproject.toml             # Updated with [jupyterlite] extra
```

## For Users

### Basic Installation

```bash
# Just Jupytext (no JupyterLite)
pip install jupytext

# With JupyterLite support
pip install jupytext[jupyterlite]
```

### Creating a JupyterLite Site

```bash
pip install jupytext[jupyterlite]
mkdir my-site && cd my-site
mkdir notebooks

# Add some .py or .md notebooks to notebooks/

jupyter lite build --contents notebooks/
jupyter lite serve
```

### Deployment

The built site in `_output/` can be deployed to any static host:
- GitHub Pages
- Netlify
- Vercel
- Cloudflare Pages
- AWS S3
- Any web server

## For Developers

### Testing the Local Extension

**Using Pixi (Recommended):**

```bash
cd jupytext

# Build and test
pixi run -e jupyterlite build-jupyterlite
pixi run -e jupyterlite serve-jupyterlite
```

**Without Pixi:**

```bash
# Install from source with jupyterlite extra
cd jupytext
pip install -e .[jupyterlite]

# Build the extension
cd jupyterlab/packages/jupyterlite-jupytext
jlpm install
jlpm build

# Try the demo
cd ../../../demo/jupyterlite-example
./build.sh
jupyter lite serve
```

### Project Structure

The JupyterLite extension lives at:
- **Source**: `jupyterlab/packages/jupyterlite-jupytext/src/`
- **Built**: `jupyterlab/packages/jupyterlite-jupytext/lib/`
- **Demo**: `demo/jupyterlite-example/`

## Benefits of This Approach

### Unified Package
- ✅ One package to install: `jupytext[jupyterlite]`
- ✅ Consistent versioning with core Jupytext
- ✅ Easier to maintain and update

### Simpler Installation
- ✅ No separate package to publish
- ✅ Standard pip extras syntax
- ✅ Works with editable installs (`pip install -e .[jupyterlite]`)

### Better Integration
- ✅ Shared code between server and browser versions
- ✅ Coordinated releases
- ✅ Single issue tracker and documentation

## Migration Path

Since this hasn't been published yet, there's nothing to migrate! Users will simply:

```bash
# Install Jupytext with JupyterLite support
pip install jupytext[jupyterlite]
```

## Technical Details

### How It Works

1. **pyproject.toml** defines the `[jupyterlite]` extra:
   ```toml
   [project.optional-dependencies]
   jupyterlite = ["jupyterlite-core>=0.2.0"]
   ```

2. **Extension lives in repo**: The TypeScript extension is at `jupyterlab/packages/jupyterlite-jupytext/`

3. **Build process**: The extension is built separately but distributed with the package

4. **Runtime**: The extension runs Jupytext Python code in Pyodide (browser)

### Dependencies

The `[jupyterlite]` extra adds:
- `jupyterlite-core` - Core JupyterLite functionality

The extension itself uses (in browser):
- Pyodide - Python in WebAssembly
- Jupytext Python code (loaded in Pyodide)

## Documentation

- **Quick Start**: [JUPYTERLITE_QUICKSTART.md](JUPYTERLITE_QUICKSTART.md)
- **Full Guide**: [docs/jupyterlite.md](docs/jupyterlite.md)
- **Implementation**: [JUPYTERLITE_IMPLEMENTATION.md](JUPYTERLITE_IMPLEMENTATION.md)
- **Demo**: [demo/jupyterlite-example/](demo/jupyterlite-example/)

## Examples

### Example 1: Simple Site

```bash
mkdir my-notebooks && cd my-notebooks
pip install jupytext[jupyterlite]

# Create a Python notebook
cat > analysis.py << 'EOF'
# %% [markdown]
# # Data Analysis

# %%
import sys
print(f"Python {sys.version}")
EOF

# Build and serve
mkdir notebooks && mv analysis.py notebooks/
jupyter lite build --contents notebooks/
jupyter lite serve
```

### Example 2: GitHub Pages

```yaml
# .github/workflows/deploy.yml
name: Deploy
on: [push]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: pip install jupytext[jupyterlite]
      - run: jupyter lite build --contents notebooks/
      - uses: actions/deploy-pages@v4
```

## Comparison: Standalone vs. Bundled

| Aspect | Standalone Package | Bundled in Jupytext |
|--------|-------------------|-------------------|
| Installation | `pip install jupyterlite-jupytext` | `pip install jupytext[jupyterlite]` |
| Versioning | Separate version | Same as Jupytext |
| Releases | Independent | Coordinated |
| Maintenance | Two packages | One package |
| Dependencies | Explicit | Via extras |

We chose the bundled approach for simplicity and better integration.

## Future Enhancements

Potential improvements:
1. Pre-built Pyodide packages for faster loading
2. Offline-first mode with bundled assets
3. Enhanced format configuration UI
4. Integration with JupyterLite's file system API
5. Support for paired notebooks in browser storage

## Support

- **Issues**: https://github.com/mwouts/jupytext/issues
- **Discussions**: https://github.com/mwouts/jupytext/discussions
- **Documentation**: https://jupytext.readthedocs.io/

## License

MIT License - Same as Jupytext main package
