# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
#   language_info:
#     codemirror_mode:
#       name: ipython
#       version: 3
#     file_extension: .py
#     mimetype: text/x-python
#     name: python
#     nbconvert_exporter: python
#     pygments_lexer: ipython3
#     version: 3.6.5
# ---

c = '''
title: "Quick test"
output:
  ioslides_presentation:
    widescreen: true
    smaller: true
editor_options:
     chunk_output_type console
'''

import yaml
print(yaml.dump(yaml.load(c)))

# next
