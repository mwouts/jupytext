---
kernelspec:
  display_name: Octave
  language: octave
  name: octave
language_info:
  file_extension: .m
  help_links:
  - text: GNU Octave
    url: https://www.gnu.org/software/octave/support.html
  - text: Octave Kernel
    url: https://github.com/Calysto/octave_kernel
  - text: MetaKernel Magics
    url: https://github.com/calysto/metakernel/blob/master/metakernel/magics/README.md
  mimetype: text/x-octave
  name: octave
  version: 4.2.2
---

A markdown cell

```{code-cell}
1 + 1
```

```{code-cell}
% a code cell with comments
2 + 2
```

```{code-cell}
% a simple plot
x = -10:0.1:10;
plot (x, sin (x));
```

```{code-cell}
%plot -w 800
% a simple plot with a magic instruction
x = -10:0.1:10;
plot (x, sin (x));
```

And to finish with, a Python cell

```{code-cell}
%%python
a = 1
```

```{code-cell}
%%python
a + 1
```
