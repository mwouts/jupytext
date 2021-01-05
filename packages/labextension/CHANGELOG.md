# 1.3.0 (2021-01-05)

- The `jupyterlab-jupytext` extension is now distributed using `jupyter-packaging`, thanks to Martin Renou's awesome contribution (#683).

# 1.2.3 (2020-10-14)

- Remove duplicate `jupyterlab` entry in `package.json` (#654)

# 1.2.2 (2020-10-13)

- The description of the `jupyterlab-jupytext` extension was updated (#654)
- The explicit dependency on the `jupytext` Python package was documented in `package.json` (#654)

# 1.2.1 (2020-03-18)

- The extension can pair a notebook to the new MyST Markdown format, developed by the [ExecutableBookProject](https://github.com/ExecutableBookProject) team. Thanks to Chris Sewell for his PRs! (#447 #456 #458)

# 1.2.0 (2020-03-09)

- This version of the extension is compatible with JupyterLab 2.0. Many thanks to Jean Helie! (#449)

# 1.1.1 (2019-12-26)

- The `nomarker` format is available through the Jupytext commands (requires `jupytext>=1.3.1`).

# 1.1.0 (2019-11-03)

- Multiple pairings are supported (#290)
- The documentation includes the last version numbers for both Jupytext Python and for this extension (#311)
- Documentation says clearly that the extension is bundled with the Python package (#350)

# 1.0.2 (2019-07-18)

- Fixed an incorrect `target_format` entry inserted by the version 1.0.1 of the extension.

# 1.0.1 (2019-07-18)

- A click on a selected format toggle the pairing (#289)
- Use `JupyterFrontEnd` and `JupyterFrontEndPlugin` from `@jupyterlab/application` rather than `JupyterLab` and `JupyterLabPlugin` for compatibility with JupyterLab 1.0.

# 1.0.0 (2019-07-06)

- First extension compatible with JupyterLab 1.0

# 0.19.0 (2019-07-06)

- Last extension compatible with JupyterLab 0.35

# 0.1.0 (2018-10-02)

- Initial release of the extension
