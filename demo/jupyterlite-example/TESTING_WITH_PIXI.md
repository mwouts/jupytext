# Testing JupyterLite with Pixi

Quick guide for testing the JupyterLite integration using pixi.

## Prerequisites

- Pixi installed: https://pixi.sh/
- Clone the Jupytext repository

## Quick Test

From the repository root:

```bash
# Build the JupyterLite demo site
pixi run -e jupyterlite build-jupyterlite

# Serve it locally
pixi run -e jupyterlite serve-jupyterlite
```

Then open http://localhost:8000 and try opening `welcome.py` as a notebook!

## What This Does

1. **`pixi run -e jupyterlite build-jupyterlite`**:
   - Uses the `jupyterlite` environment (has jupyterlite-core installed)
   - Installs jupytext with jupyterlite extra
   - Builds the TypeScript extension (jupyterlite-jupytext)
   - Runs `jupyter lite build` to create the site

2. **`pixi run -e jupyterlite serve-jupyterlite`**:
   - Serves the built site at http://localhost:8000
   - No server-side processing - all static files

## Manual Steps (Alternative)

If you prefer to work interactively:

```bash
# Enter the jupyterlite environment
pixi shell -e jupyterlite

# Now you're in a shell with all dependencies
cd demo/jupyterlite-example

# Build (if not already done)
../../build.sh  # or manually: jupyter lite build --contents notebooks/

# Serve
jupyter lite serve
```

## Troubleshooting

### "Command not found: jlpm"

If the build script fails because `jlpm` is not found:

```bash
# Install yarn globally (jlpm is provided by jupyterlab)
pixi run -e jupyterlite npm install -g yarn

# Or ensure jupyterlab is installed
pixi install -e jupyterlite
```

### Build is slow

The first build takes a while because:
- Node dependencies need to be installed (`jlpm install`)
- TypeScript needs to be compiled
- JupyterLite assets need to be generated

Subsequent builds are faster.

### "Not in a pixi environment"

If you see this error from build.sh, you forgot to use pixi:

```bash
# Wrong:
cd demo/jupyterlite-example
./build.sh

# Right:
pixi run -e jupyterlite build-jupyterlite
```

## Testing Your Changes

After making changes to the extension:

```bash
# Rebuild everything
pixi run -e jupyterlite build-jupyterlite

# Serve and test
pixi run -e jupyterlite serve-jupyterlite
```

## What's Different from Pip?

| Aspect | Pip | Pixi |
|--------|-----|------|
| Environment | Uses system Python or venv | Uses conda-forge packages |
| Package management | requirements.txt | pyproject.toml |
| Consistency | May vary by system | Reproducible across systems |
| Speed | Depends on system | Fast with caching |
| Node.js | Must install separately | Included in environment |

Pixi is recommended for development because it ensures everyone has the same environment.
