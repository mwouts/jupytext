---
kernelspec:
  display_name: Stata
  language: stata
  name: stata
language_info:
  codemirror_mode: stata
  file_extension: .do
  mimetype: text/x-stata
  name: stata
  version: '15.1'
---

```{code-cell}
// This notebook uses the stata_kernel: https://github.com/kylebarron/stata_kernel
```

```{code-cell}
use http://www.stata-press.com/data/r13/auto
```

```{code-cell}
summarize
```

```{code-cell}
scatter weight length
```
