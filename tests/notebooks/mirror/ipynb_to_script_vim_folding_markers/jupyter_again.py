# ---
# jupyter:
#   jupytext:
#     cell_markers: '{{{,}}}'
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
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

# ?next
