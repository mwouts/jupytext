---
kernelspec:
  display_name: Wolfram Language 13.1
  language: Wolfram Language
  name: wolframlanguage13.1
---

**Note:** The `language_info` `file_extension` in this notebook should be `.m`, but it was deliberately changed to `.wolfram` to avoid conflicts with Matlab which is using the same extension.

+++

We start with...

```{code-cell} mathematica
Print["Hello, World!"];
```

Then we draw the first example plot from the [ListPlot](https://reference.wolfram.com/language/ref/ListPlot.html) reference:

```{code-cell} mathematica
ListPlot[Prime[Range[25]]]
```

We also test the math outputs as in the [Simplify](https://reference.wolfram.com/language/ref/Simplify.html) example:

```{code-cell} mathematica
D[Integrate[1/(x^3 + 1), x], x]
```
