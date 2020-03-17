---
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

```{code-cell} ipython3
c = '''
title: "Quick test"
output:
  ioslides_presentation:
    widescreen: true
    smaller: true
editor_options:
     chunk_output_type console
'''
```

```{code-cell} ipython3
import yaml
print(yaml.dump(yaml.load(c)))
```

```{code-cell} ipython3
?next
```
