"""Find kernel specifications for a given language"""

import sys
from jupyter_client.kernelspec import find_kernel_specs, get_kernel_spec


def set_kernelspec_from_language(notebook):
    """Set the kernel specification based on the 'main_language' metadata"""
    language = notebook.metadata.get('jupytext', {}).get('main_language')
    if 'kernelspec' not in notebook.metadata and language:
        kernelspec = kernelspec_from_language(language)
        if kernelspec:
            notebook.metadata['kernelspec'] = kernelspec
            notebook.metadata.get('jupytext', {}).pop('main_language')


def kernelspec_from_language(language):
    """Return the python kernel that matches the current env, or the first kernel that matches the given language"""
    try:
        if language == 'python':
            # Return the kernel that matches the current Python executable
            for name in find_kernel_specs():
                kernel_specs = get_kernel_spec(name)
                if kernel_specs.language == 'python' and kernel_specs.argv[0] == sys.executable:
                    return {'name': name, 'language': language, 'display_name': kernel_specs.display_name}

        for name in find_kernel_specs():
            kernel_specs = get_kernel_spec(name)
            if kernel_specs.language == language or (language == 'c++' and kernel_specs.language.startswith('C++')):
                return {'name': name, 'language': language, 'display_name': kernel_specs.display_name}
    except (KeyError, ValueError):
        pass
    return None
