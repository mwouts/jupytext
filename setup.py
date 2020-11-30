from os import path
from io import open
import re
from setuptools import setup, find_packages

from jupyter_packaging import (
    create_cmdclass,
    install_npm,
    ensure_targets,
    combine_commands,
)

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    # replace Markdown links (docs/[NAME].md with (https://jupytext.readthedocs.io/en/latest/[NAME].html
    long_description = re.sub(
        r"\(docs/([A-Za-z-_]*).md",
        "(https://jupytext.readthedocs.io/en/latest/\\1.html",
        f.read(),
    )

with open(path.join(this_directory, "jupytext/version.py")) as f:
    version_file = f.read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    version = version_match.group(1)

lab_path = path.join(this_directory, "jupytext", "labextension")
nb_path = path.join(this_directory, "jupytext", "nbextension")

jupyter_config_path = path.join(this_directory, "jupyter-config")
notebook_config_path = path.join(jupyter_config_path, "jupyter_notebook_config.d")
jupyter_server_config_path = path.join(jupyter_config_path, "jupyter_server_config.d")
nbconfig_path = path.join(jupyter_config_path, "nbconfig", "notebook.d")

data_files_spec = [
    # Install labextension
    ("share/jupyter/labextensions/jupyterlab-jupytext", lab_path, "**"),
    ("share/jupyter/labextensions/jupyterlab-jupytext", this_directory, "install.json"),
    # Install nbextension
    ("share/jupyter/nbextensions/jupytext", nb_path, "**"),
    ("share/jupyter/nbextensions/jupytext", nbconfig_path, "jupytext.json"),
    # Install config files
    (
        "etc/jupyter/jupyter_server_config.d",
        jupyter_server_config_path,
        "jupytext.json",
    ),
    ("etc/jupyter/jupyter_notebook_config.d", notebook_config_path, "jupytext.json"),
    ("etc/jupyter/nbconfig/notebook.d", nbconfig_path, "jupytext.json"),
]

# Representative files that should exist after a successful build
jstargets = [
    path.join(lab_path, "package.json"),
]

cmdclass = create_cmdclass(
    "jsdeps",
    package_data_spec={"jupytext": ["nbextension/**"]},
    data_files_spec=data_files_spec,
)

cmdclass["jsdeps"] = combine_commands(
    install_npm(
        path.join(this_directory, "packages", "labextension"),
        build_cmd="build:prod",
        npm=["jlpm"],
    ),
    ensure_targets(jstargets),
)

setup(
    name="jupytext",
    version=version,
    author="Marc Wouts",
    author_email="marc.wouts@gmail.com",
    description="Jupyter notebooks as Markdown documents, "
    "Julia, Python or R scripts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mwouts/jupytext",
    packages=find_packages(exclude=["tests"]),
    cmdclass=cmdclass,
    entry_points={"console_scripts": ["jupytext = jupytext.cli:jupytext"]},
    tests_require=["pytest"],
    install_requires=["nbformat>=4.0.0", "pyyaml", "toml", "markdown-it-py~=0.6.0"],
    python_requires="~=3.6",
    extras_require={
        # left for back-compatibility
        "myst": [],
        "toml": ["toml"],
        "rst2md": ["sphinx-gallery~=0.7.0"],
    },
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Environment :: Console",
        "Framework :: Jupyter",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Text Processing :: Markup",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
