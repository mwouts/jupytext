---
jupyter:
  kernelspec:
    display_name: Coconut
    language: coconut
    name: coconut
---

Taken from [coconut-lang.org](coconut-lang.org)


pipeline-style programming

```coconut
"hello, world!" |> print
```

 prettier lambdas

```coconut
x -> x ** 2
```

partial application

```coconut
range(10) |> map$(pow$(?, 2)) |> list
```

pattern-matching

```coconut
match [head] + tail in [0, 1, 2, 3]:
    print(head, tail)
```

destructuring assignment

```coconut
{"list": [0] + rest} = {"list": [0, 1, 2, 3]}
```

infix notation

```coconut
# 5 `mod` 3 == 2
```

operator functions

```coconut
product = reduce$(*)
```

function composition

```coconut
# (f..g..h)(x, y, z)
```

lazy lists

```coconut
# (| first_elem() |) :: rest_elems()
```

parallel programming

```coconut
range(100) |> parallel_map$(pow$(2)) |> list
```

tail call optimization

```coconut
def factorial(n, acc=1):
    case n:
        match 0:
            return acc
        match _ is int if n > 0:
            return factorial(n-1, acc*n)
```

algebraic data types

```coconut
data Empty()
data Leaf(n)
data Node(l, r)

def size(Empty()) = 0

addpattern def size(Leaf(n)) = 1

addpattern def size(Node(l, r)) = size(l) + size(r)
```

and much more!

Like what you see? Don't forget to star Coconut on GitHub!

```coconut

```
