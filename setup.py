import re
import warnings
from io import open
from os import environ, path

from setuptools import find_packages, setup

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

setup_args = dict(
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
    entry_points={"console_scripts": ["jupytext = jupytext.cli:jupytext"]},
    tests_require=["pytest"],
    install_requires=[
        "nbformat",
        "pyyaml",
        "toml",
        "markdown-it-py~=1.0",
        "mdit_py_plugins",
    ],
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

build_labextension = environ.get("BUILD_JUPYTERLAB_EXTENSION")
if build_labextension in ["0", "False", "false", "No", "no", "N", "n"]:
    build_labextension = False

if not build_labextension:
    # We skip the lab extension,
    # cf. https://github.com/mwouts/jupytext/issues/706
    warnings.warn(
        "Jupytext is being built WITHOUT the lab extension. "
        "Please set BUILD_JUPYTERLAB_EXTENSION=1 if you want it."
    )

    setup_args["package_data"] = {"jupytext": ["nbextension/*.*"]}
    setup_args["data_files"] = [
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
    ]
else:
    # Install labextension using jupyter_packaging
    from jupyter_packaging import (
        combine_commands,
        create_cmdclass,
        ensure_targets,
        install_npm,
    )

    lab_path = path.join(this_directory, "jupytext", "labextension")
    nb_path = path.join(this_directory, "jupytext", "nbextension")

    jupyter_config_path = path.join(this_directory, "jupyter-config")
    notebook_config_path = path.join(jupyter_config_path, "jupyter_notebook_config.d")
    jupyter_server_config_path = path.join(
        jupyter_config_path, "jupyter_server_config.d"
    )
    nbconfig_path = path.join(jupyter_config_path, "nbconfig", "notebook.d")

    data_files_spec = [
        # Install nbextension
        ("share/jupyter/nbextensions/jupytext", nb_path, "**"),
        ("share/jupyter/nbextensions/jupytext", nbconfig_path, "jupytext.json"),
        # Install config files
        (
            "etc/jupyter/jupyter_server_config.d",
            jupyter_server_config_path,
            "jupytext.json",
        ),
        (
            "etc/jupyter/jupyter_notebook_config.d",
            notebook_config_path,
            "jupytext.json",
        ),
        ("etc/jupyter/nbconfig/notebook.d", nbconfig_path, "jupytext.json"),
        ("share/jupyter/labextensions/jupyterlab-jupytext", lab_path, "**"),
        (
            "share/jupyter/labextensions/jupyterlab-jupytext",
            this_directory,
            "install.json",
        ),
    ]
    package_data_spec = {"jupytext": ["nbextension/**"]}

    # Representative files that should exist after a successful build
    jstargets = [
        path.join(lab_path, "package.json"),
    ]

    cmdclass = create_cmdclass(
        "jsdeps",
        package_data_spec=package_data_spec,
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
    setup_args["cmdclass"] = cmdclass

# Call setup
setup(**setup_args)
