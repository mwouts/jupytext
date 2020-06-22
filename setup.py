from os import path
from io import open
import re
from setuptools import setup, find_packages

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

with open(path.join(this_directory, "jupytext/version.py")) as f:
    version_file = f.read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    version = version_match.group(1)

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
    package_data={"jupytext": ["nbextension/*.*"]},
    data_files=[
        (
            "etc/jupyter/nbconfig/notebook.d",
            ["jupyter-config/nbconfig/notebook.d/jupytext.json"],
        ),
        (
            "etc/jupyter/jupyter_notebook_config.d",
            ["jupyter-config/jupyter_notebook_config.d/jupytext.json"],
        ),
        (
            "etc/jupyter/jupyter_server_config.d",
            ["jupyter-config/jupyter_server_config.d/jupytext.json"],
        ),
        (
            "share/jupyter/nbextensions/jupytext",
            [
                "jupytext/nbextension/index.js",
                "jupytext/nbextension/README.md",
                "jupytext/nbextension/jupytext_menu.png",
                "jupytext/nbextension/jupytext.yml",
            ],
        ),
        (
            "share/jupyter/lab/extensions",
            ["packages/labextension/jupyterlab-jupytext-1.2.1.tgz"],
        ),
    ],
    entry_points={"console_scripts": ["jupytext = jupytext.cli:jupytext"]},
    tests_require=["pytest"],
    install_requires=["nbformat>=4.0.0", "pyyaml", "toml", 'mock;python_version<"3"'],
    extras_require={
        "myst": ["myst-parser~=0.8; python_version >= '3.6'"],
        "toml": ["toml"],
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
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
)
