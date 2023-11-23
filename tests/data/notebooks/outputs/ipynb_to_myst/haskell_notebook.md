---
kernelspec:
  display_name: Haskell
  language: haskell
  name: haskell
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
