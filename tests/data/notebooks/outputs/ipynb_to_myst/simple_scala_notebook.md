---
kernelspec:
  display_name: Apache Toree - Scala
  language: scala
  name: apache_toree_scala
language_info:
  codemirror_mode: text/x-scala
  file_extension: .scala
  mimetype: text/x-scala
  name: scala
  pygments_lexer: scala
  version: 2.11.12
---

```{code-cell} scala
// This is just a simple scala notebook

object SampleObject {
    def calculation(x: Int, y: Int): Int = x + y
}

val result = SampleObject.calculation(1, 2)
```

```{code-cell} scala
println(result * 10)
```
