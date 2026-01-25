# Jupytext for JupyterLite

> **Note**: This extension is included in the main Jupytext package as an optional feature.
> Install with `pip install jupytext[jupyterlite]`.

This extension brings [Jupytext](https://github.com/mwouts/jupytext) functionality to [JupyterLite](https://jupyterlite.readthedocs.io/), enabling you to work with notebooks in text formats (Python, R, Markdown, etc.) directly in your browser!

## Testing Locally

To test this extension before it's published:

1. **Build the extension**:
   ```bash
   cd jupyterlab/packages/jupyterlite-jupytext
   jlpm install
   jlpm build
   ```

2. **Try the demo**:
   ```bash
   cd ../../../demo/jupyterlite-example
   pip install -r requirements.txt
   ./build.sh
   jupyter lite serve
   ```

3. Open http://localhost:8000 and try opening `welcome.py` as a notebook!

## Overview

JupyterLite runs entirely in the browser using WebAssembly, which means traditional server-side Jupyter extensions don't work. This extension solves that problem by:

1. **Running Jupytext in the browser**: Uses [Pyodide](https://pyodide.org/) (Python compiled to WebAssembly) to run Jupytext's conversion code directly in your browser
2. **Transparent conversion**: Automatically converts between `.ipynb` and text formats (`.py`, `.md`, `.R`, etc.) when you open and save files
3. **No server required**: Everything happens client-side, perfect for JupyterLite deployments

## Features

- ✅ Open `.py`, `.R`, `.jl`, `.md`, and other text files as Jupyter notebooks
- ✅ Save notebooks in text formats for better version control
- ✅ Automatic format detection based on file extension
- ✅ Support for multiple Jupytext formats (percent, light, markdown, etc.)
- ✅ Works entirely in the browser - no server needed
- ✅ Compatible with existing Jupytext notebook metadata

## Supported Formats

- **Python**: `.py` (percent, light, nomarker formats)
- **R**: `.R`, `.r` (percent, light formats)
- **Julia**: `.jl` (percent, light formats)
- **Markdown**: `.md` (standard markdown)
- **R Markdown**: `.Rmd`
- **Quarto**: `.qmd`
- **MyST Markdown**: `.md` (MyST format)
- And many other languages supported by Jupytext!

## Installation

### For JupyterLite Site Builders

To add Jupytext support to your JupyterLite deployment:

1. Install the extension package:
   ```bash
   pip install jupyterlite-jupytext
   ```

2. Add it to your JupyterLite build:
   ```bash
   jupyter lite build --contents your_content_folder
   ```

3. The extension will automatically load when users visit your JupyterLite site.

### For Development

1. Clone the Jupytext repository:
   ```bash
   git clone https://github.com/mwouts/jupytext.git
   cd jupytext/jupyterlab/packages/jupyterlite-jupytext
   ```

2. Install dependencies:
   ```bash
   jlpm install
   ```

3. Build the extension:
   ```bash
   jlpm build
   ```

4. Link it to your JupyterLite development environment.

## How It Works

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     JupyterLite (Browser)                    │
├─────────────────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────────────────┐  │
│  │          Jupytext Extension (TypeScript)              │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │    Contents Manager Wrapper                     │  │  │
│  │  │    - Intercepts file open/save operations       │  │  │
│  │  │    - Detects text notebook formats              │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  │                         ↕                             │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │    Pyodide Converter (Python in WASM)           │  │  │
│  │  │    - Runs actual Jupytext Python code           │  │  │
│  │  │    - Converts: notebook ⟷ text                  │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Conversion Flow

1. **Opening a file**:
   - User opens `notebook.py` in JupyterLite
   - Contents manager detects it's a text notebook
   - Pyodide converter runs `jupytext.reads(text, fmt='py:percent')`
   - Notebook is displayed in the browser

2. **Saving a file**:
   - User saves changes to the notebook
   - Contents manager intercepts the save operation
   - Pyodide converter runs `jupytext.writes(notebook, fmt='py:percent')`
   - Text file is saved to the browser storage

## Usage

Once installed, the extension works automatically:

1. **Open a text notebook**: Right-click any `.py`, `.md`, `.R`, etc. file and select "Open With → Notebook"

2. **Create a new text notebook**: Use the Jupyter interface to create a new notebook, then save it with a text extension (e.g., `my_notebook.py`)

3. **Edit in text or notebook format**: Changes are transparently converted between formats

## Configuration

The extension can be configured through JupyterLab's settings:

- **Default Format**: Choose the default format for new text notebooks
- **Auto Convert**: Enable/disable automatic conversion
- **Format Detection**: Customize how file formats are detected

## Limitations

- **First load time**: The first time you use Jupytext, it needs to download and initialize Pyodide (~30MB). Subsequent uses are much faster thanks to browser caching.
- **Pyodide compatibility**: Only works in browsers that support WebAssembly
- **Performance**: Conversion happens in the browser, so very large notebooks may be slower than server-side Jupytext

## Troubleshooting

### Jupytext not loading

If you see "Pyodide not available" in the console:
- Ensure you're using a modern browser with WebAssembly support
- Check your browser console for detailed error messages
- Make sure you have a stable internet connection (needed to download Pyodide on first use)

### Conversion errors

If files aren't converting properly:
- Check that the file extension is supported
- Verify the file has valid Jupytext metadata in the header
- Look at the browser console for detailed error messages

## Development

### Building

```bash
jlpm install
jlpm build
```

### Testing

To test the extension locally:

1. Build JupyterLite with the extension
2. Serve it locally: `python -m http.server 8000`
3. Open `http://localhost:8000` in your browser
4. Try opening/saving text notebooks

## Contributing

Contributions are welcome! This extension is part of the main Jupytext project. See the [Jupytext contributing guide](https://github.com/mwouts/jupytext/blob/main/docs/contributing.md) for details.

## License

MIT License - see the main Jupytext [LICENSE](https://github.com/mwouts/jupytext/blob/main/LICENSE) file.

## Credits

- **Jupytext**: Created and maintained by [Marc Wouts](https://github.com/mwouts)
- **JupyterLite**: Developed by the [JupyterLite team](https://github.com/jupyterlite/jupyterlite)
- **Pyodide**: The amazing [Pyodide project](https://pyodide.org/) that makes Python in the browser possible

## Related Projects

- [Jupytext](https://github.com/mwouts/jupytext) - The main Jupytext project for Jupyter Server
- [JupyterLite](https://github.com/jupyterlite/jupyterlite) - Jupyter running entirely in the browser
- [Pyodide](https://github.com/pyodide/pyodide) - Python compiled to WebAssembly
