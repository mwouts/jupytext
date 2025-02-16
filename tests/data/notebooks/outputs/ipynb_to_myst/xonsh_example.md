---
kernelspec:
  display_name: Xonsh
  language: xonsh
  name: xonsh
language_info:
  codemirror_mode: shell
  file_extension: .xsh
  mimetype: text/x-sh
  name: xonsh
  pygments_lexer: xonsh
  version: 0.14.4
---

```{code-cell} xonsh
len($(curl -L https://xon.sh))
```

```{code-cell} xonsh
for filename in `.*`:
    print(filename)
    du -sh @(filename)
```
