---
jupytext:
  encoding: '// -*- coding: utf-8 -*-'
  formats: ipynb,groovy:light
kernelspec:
  display_name: Groovy
  language: groovy
  name: groovy
---

# TailRecursive annotation

Let's check what is the effect of `@TailRecursive` annotation on the simple recursive definition of factorial function.

```{code-cell}
import groovy.transform.CompileStatic
import groovy.transform.TailRecursive
import groovy.transform.TypeChecked

@CompileStatic
@TypeChecked
class X {
    static final BigInteger factorial0(int n) {
        (n <= 1) ? 1G : factorial0(n-1).multiply(BigInteger.valueOf(n))
    }

    static final BigInteger factorial1(int n, BigInteger acc = 1G) {
        (n <= 1) ? acc : factorial1(n-1, acc.multiply(BigInteger.valueOf(n)))
    }

    @TailRecursive
    static final BigInteger factorial2(int n, BigInteger acc = 1G) {
        (n <= 1) ? acc : factorial2(n-1, acc.multiply(BigInteger.valueOf(n)))
    }
}

x = new X()
```

Although we can time the execution of the calls, it is not very accurate; such micro benchmarks should be performed in more controlled environment, such us under [JMH](https://openjdk.java.net/projects/code-tools/jmh/).

For example, see [blog posts of Szymon Stępniak](https://e.printstacktrace.blog/tail-recursive-methods-in-groovy/).

```{code-cell}
%%timeit

x.factorial0(19_000).toString().length()
```

```{code-cell}
%%timeit

x.factorial1(19_000).toString().length()
```

```{code-cell}
%%timeit

x.factorial2(19_000).toString().length()
```

The real difference is the use of stack. Non-tail recursive calls exhaust the stack space at some point, whereas tail recursive calls don't add frames to the stack.

```{code-cell}
factSize = { n, cl ->
    println "Factorial of ${n} has ${cl(n).toString().length()} digits"
}

factSize 2_000, x.&factorial0
factSize 2_000, x.&factorial1
factSize 2_000, x.&factorial2

factSize 100_000, x.&factorial2
```

```{code-cell}
try {
    factSize 100_000, x.&factorial1
} catch (Throwable e) {
    assert e instanceof StackOverflowError
    println e
}
```
