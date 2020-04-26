// -*- coding: utf-8 -*-
// ---
// jupyter:
//   jupytext:
//     formats: ipynb,java:light
//   kernelspec:
//     display_name: Java
//     language: java
//     name: java
// ---

// Let's define some class.

class A {
    public void hello() {
        System.out.println("Hello World");
    }   
}

// And now we call its method.

new A().hello();

// You can run it e.g. with `jshell`
//
// * from command line, as `jshell simple-helloworld.java`
// * from jshell's shell with `/open simple-helloworld.java`
