---
kernelspec:
  display_name: Maxima
  language: maxima
  name: maxima
language_info:
  codemirror_mode: maxima
  file_extension: .mac
  mimetype: text/x-maxima
  name: maxima
  pygments_lexer: maxima
  version: 5.43.2
---

## maxima misc

```{code-cell} maxima
kill(all)$
```

```{code-cell} maxima
f(x) := 1/(x^2+l^2)^(3/2);
```

```{code-cell} maxima
integrate(f(x), x);
```

```{code-cell} maxima
tex(%)$
```

```{code-cell} maxima

```
