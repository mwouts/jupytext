"""Find kernel specifications for a given language"""

import os
import sys

from .languages import same_language
from .reraise import reraise

try:
    # I prefer not to take a dependency on jupyter_client
    from jupyter_client.kernelspec import find_kernel_specs, get_kernel_spec
except ImportError as err:
    find_kernel_specs = reraise(err)
    get_kernel_spec = reraise(err)


def set_kernelspec_from_language(notebook):
    """Set the kernel specification based on the 'main_language' metadata"""
    language = notebook.metadata.get("jupytext", {}).get("main_language")
    if "kernelspec" not in notebook.metadata and language:
        try:
            kernelspec = kernelspec_from_language(language)
        except ValueError:
            return
        notebook.metadata["kernelspec"] = kernelspec
        notebook.metadata.get("jupytext", {}).pop("main_language")


def kernelspec_from_language(language):
    """Return the python kernel that matches the current env, or the first kernel that matches the given language"""
    if language == "python":
        # Return the kernel that matches the current Python executable
        for name in find_kernel_specs():
            kernel_specs = get_kernel_spec(name)
            cmd = kernel_specs.argv[0]
            if (
                kernel_specs.language == "python"
                and os.path.isfile(cmd)
                and os.path.samefile(cmd, sys.executable)
            ):
                return {
                    "name": name,
                    "language": language,
                    "display_name": kernel_specs.display_name,
                }
        raise ValueError(
            "No kernel found that matches the current python executable {}\n".format(
                sys.executable
            )
            + "Install one with 'python -m ipykernel install --name kernel_name [--user]'"
        )

    for name in find_kernel_specs():
        kernel_specs = get_kernel_spec(name)
        if same_language(kernel_specs.language, language):
            return {
                "name": name,
                "language": language,
                "display_name": kernel_specs.display_name,
            }

    raise ValueError(f"No kernel found for the language {language}")
