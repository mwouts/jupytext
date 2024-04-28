---
kernelspec:
  display_name: Xonsh
  language: xonsh
  name: xonsh
---

```{code-cell} xonsh
len($(curl -L https://xon.sh))
```

```{code-cell} xonsh
for filename in `.*`:
    print(filename)
    du -sh @(filename)
```
