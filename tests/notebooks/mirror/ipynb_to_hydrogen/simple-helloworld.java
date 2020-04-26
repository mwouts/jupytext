// -*- coding: utf-8 -*-
// ---
// jupyter:
//   jupytext:
//     formats: ipynb,java:hydrogen
//   kernelspec:
//     display_name: Java
//     language: java
//     name: java
// ---

// %% [markdown]
// Let's define some class.

// %%
class A {
    public void hello() {
        System.out.println("Hello World");
    }   
}

// %% [markdown]
// And now we call its method.

// %%
new A().hello();

// %% [markdown]
// You can run it e.g. with `jshell`
//
// * from command line, as `jshell simple-helloworld.java`
// * from jshell's shell with `/open simple-helloworld.java`
