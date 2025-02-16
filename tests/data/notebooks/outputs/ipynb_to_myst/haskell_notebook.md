---
kernelspec:
  display_name: Haskell
  language: haskell
  name: haskell
language_info:
  codemirror_mode: ihaskell
  file_extension: .hs
  mimetype: text/x-haskell
  name: haskell
  pygments_lexer: Haskell
  version: 8.10.7
---

# Example Haskell Notebook

+++

Define a function to add two numbers.

```{code-cell} Haskell
f :: Num a => a -> a -> a
f x y = x + y
```

Try to use the function

```{code-cell} Haskell
f 1 2 
```
