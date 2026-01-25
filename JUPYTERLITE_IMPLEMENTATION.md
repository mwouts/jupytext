# Jupytext for JupyterLite - Implementation Summary

This document describes the JupyterLite support that has been included in Jupytext.

> **Note**: The JupyterLite extension is bundled as part of the main Jupytext package.
> Install with `pip install jupytext[jupyterlite]` to enable JupyterLite support.

## Overview

JupyterLite runs entirely in the browser using WebAssembly, which means traditional server-side Jupyter extensions don't work. This implementation provides a client-side alternative that runs Jupytext in the browser using Pyodide (Python compiled to WebAssembly).

## What Was Created

### 1. Core Extension Package (`jupyterlab/packages/jupyterlite-jupytext/`)

A new JupyterLab extension package that provides:

- **`converter.ts`**: Pyodide-based converter that runs Jupytext Python code in the browser
- **`contents.ts`**: Contents manager wrapper that intercepts file operations
- **`utils.ts`**: Utility functions for format detection and file type handling
- **`index.ts`**: Main extension plugin that ties everything together
- **`package.json`**: Package configuration with dependencies
- **`tsconfig.json`**: TypeScript configuration
- **`schema/plugin.json`**: Extension settings schema

### 2. Documentation

- **`docs/jupyterlite.md`**: Comprehensive guide for using Jupytext with JupyterLite
- **`jupyterlab/packages/jupyterlite-jupytext/README.md`**: Extension-specific README

### 3. Demo/Example

- **`demo/jupyterlite-example/`**: Complete example project showing how to deploy JupyterLite with Jupytext
  - Configuration files (`jupyter-lite.json`, `requirements.txt`)
  - Sample notebook (`notebooks/welcome.py`)
  - GitHub Actions workflow for deployment
  - Comprehensive README

## How It Works

### Architecture

```
┌─────────────────────────────────────────┐
│         Browser (JupyterLite)            │
├─────────────────────────────────────────┤
│  TypeScript Extension Layer              │
│  ┌──────────────────────────────────┐   │
│  │  Contents Manager Wrapper         │   │
│  │  - Detects text notebook files    │   │
│  │  - Intercepts get/save operations │   │
│  └──────────────────────────────────┘   │
│              ↓ ↑                         │
│  ┌──────────────────────────────────┐   │
│  │  Pyodide Converter                │   │
│  │  - Loads Jupytext in WASM         │   │
│  │  - Runs Python conversion code    │   │
│  │  - Returns converted content      │   │
│  └──────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

### Conversion Flow

1. **File Open**:
   - User opens `notebook.py`
   - Contents manager detects it's a text notebook
   - Converter calls `jupytext.reads(text, 'py:percent')` in Pyodide
   - Returns notebook JSON to JupyterLab

2. **File Save**:
   - User saves notebook
   - Contents manager intercepts save
   - Converter calls `jupytext.writes(notebook, 'py:percent')` in Pyodide
   - Saves text representation

## Key Features

✅ **Client-side conversion**: All conversion happens in the browser
✅ **No server required**: Perfect for static site deployments
✅ **Automatic format detection**: Based on file extension
✅ **Multiple format support**: Python, R, Julia, Markdown, etc.
✅ **Transparent operation**: Users don't need to know about conversion
✅ **Offline capable**: Works after initial Pyodide download

## Setup Instructions

### For Extension Developers

1. Navigate to the extension directory:
   ```bash
   cd jupyterlab/packages/jupyterlite-jupytext
   ```

2. Install dependencies:
   ```bash
   jlpm install
   ```

3. Build the extension:
   ```bash
   jlpm build
   ```

4. The extension can then be included in a JupyterLite build.

### For Site Builders

**Current (using local source)**:

```bash
# From the demo directory
cd jupytext/demo/jupyterlite-example
pip install -r requirements.txt
./build.sh
jupyter lite serve
```

**After publishing**:

```bash
pip install jupyterlite-core jupyterlite-jupytext
jupyter lite build --contents notebooks/
jupyter lite serve
```

See the demo in `demo/jupyterlite-example/` for a complete working example

4. Deploy the `_output/` directory to any static host.

### Using the Demo

The `demo/jupyterlite-example/` directory contains a complete working example:

```bash
cd demo/jupyterlite-example/
pip install -r requirements.txt
jupyter lite build
jupyter lite serve
```

Then open http://localhost:8000 and try opening `welcome.py` as a notebook!

## Deployment Options

### GitHub Pages

Use the provided `.github/workflows/deploy.yml` workflow. It will:
1. Build JupyterLite with Jupytext
2. Deploy to GitHub Pages automatically on push

### Other Static Hosts

The extension works with any static file host:
- Netlify
- Vercel
- Cloudflare Pages
- AWS S3 + CloudFront
- Any simple HTTP server

Just deploy the `_output/` directory after building.

## Limitations

### Technical Constraints

1. **Initial load time**: First use requires downloading Pyodide (~30MB)
2. **Memory usage**: Pyodide requires significant browser memory
3. **No paired notebooks**: Automatic pairing not supported (no persistent server)
4. **No pre-commit hooks**: Can't run Git hooks in the browser

### When to Use Server-side vs. Browser-side

**Use server-side Jupytext** (traditional extension) when:
- You need paired notebooks with automatic sync
- You want pre-commit hook integration
- You have a Jupyter server available
- Performance is critical for very large notebooks

**Use browser-side Jupytext** (this implementation) when:
- Deploying to static hosting
- No server infrastructure available
- Sharing notebooks via simple URLs
- Teaching/demos where easy access is important
- Creating offline-capable notebook sites

## Testing

### Manual Testing

1. Build the extension
2. Create a JupyterLite site with the extension
3. Test scenarios:
   - Open `.py` file as notebook
   - Edit and save notebook
   - Try different formats (`.md`, `.R`, etc.)
   - Check conversion accuracy
   - Verify browser console for errors

### Browser Compatibility

Tested on:
- ✅ Chrome/Edge (Chromium-based)
- ✅ Firefox
- ✅ Safari (WebKit)

Requires:
- WebAssembly support
- Modern JavaScript (ES2020+)
- ~200MB available memory

## Future Enhancements

Potential improvements for future versions:

1. **Offline-first design**: Bundle Pyodide locally
2. **Progressive loading**: Load Jupytext modules on-demand
3. **Worker threads**: Run conversion in Web Workers for better performance
4. **Format configuration UI**: GUI for selecting formats
5. **Bulk operations**: Convert multiple files at once
6. **Format preview**: Show text representation without saving

## Troubleshooting

### Extension Not Loading

**Check**:
- Browser console for errors
- Extension is in JupyterLite extension list
- Pyodide loads successfully (watch Network tab)

**Common Issues**:
- CORS problems: Ensure proper headers for WebAssembly
- Memory limits: Close other tabs to free memory
- Cache issues: Clear browser cache and reload

### Conversion Failures

**Check**:
- File syntax is valid (e.g., valid Python)
- File has proper Jupytext markers
- Browser console for Python errors

**Debug**:
```javascript
// In browser console:
const converter = window.jupytextConverter;
await converter.ready;
// Try manual conversion to see errors
```

## Contributing

To contribute to the JupyterLite extension:

1. Fork the Jupytext repository
2. Create a branch for your changes
3. Make changes in `jupyterlab/packages/jupyterlite-jupytext/`
4. Test thoroughly with JupyterLite
5. Submit a pull request

See [CONTRIBUTING.md](../CONTRIBUTING.md) for general guidelines.

## Credits

This implementation builds on:
- **Jupytext**: The core notebook conversion library by Marc Wouts
- **JupyterLite**: Browser-based Jupyter by the JupyterLite team
- **Pyodide**: Python in WebAssembly by the Pyodide team

## License

MIT License - Same as Jupytext main project.

## Learn More

- [Jupytext Documentation](https://jupytext.readthedocs.io/)
- [JupyterLite Documentation](https://jupyterlite.readthedocs.io/)
- [Pyodide Documentation](https://pyodide.org/)
- [WebAssembly](https://webassembly.org/)
