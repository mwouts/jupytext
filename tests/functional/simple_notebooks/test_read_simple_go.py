import jupytext
from jupytext.compare import compare


def test_read_simple_file(
    go="""// -*- coding: utf-8 -*-
// ---
// jupyter:
//   kernelspec:
//     display_name: Go (gonb)
//     language: go
//     name: gonb
// ---

// A notebook that use [GoNB](https://github.com/janpfeifer/gonb)

// the code below comes from [tutorial.ipynb](https://github.com/janpfeifer/gonb/blob/main/examples/tutorial.ipynb)

func main() {
    fmt.Printf("Hello World!")
}
""",
):
    nb = jupytext.reads(go, "go:light")
    assert len(nb.cells) == 3
    assert nb.cells[0].cell_type == "markdown"
    assert nb.cells[1].cell_type == "markdown"
    assert nb.cells[2].cell_type == "code"


def test_read_go_notebook_with_percent_percent_and_arguments(
    go="""// %% [markdown]
// # Square Function
//
// Defines a function $f(x) = x^2$

// %%
func Square(x float64) float64 {
        return x*x
}

// %% [markdown]
// # Examples
//
// ## Example A: $x = 3$

// %%
var x = flag.Float64("x", 0.0, "value of x to feed f(x)")

//gonb:%% -x=3
fmt.Printf("Square(%g)=%g\n", *x, Square(*x))

// %% [markdown]
// ## Example B: $x = 4$

// %%
//gonb:%% -x=4
fmt.Printf("Square(%g)=%g\n", *x, Square(*x))
""",
):
    nb = jupytext.reads(go, "go")
    for cell in nb.cells:
        assert "gonb" not in cell.source, cell.source

    go2 = jupytext.writes(nb, "go")
    compare(go2, go)


def test_read_go_notebook_with_magic_main(
    go="""// %%
package square

// %% [markdown]
// # Defining a $x^2$ function
// It returns x*x.

// %%
func Square(x float64) float64 {
  return x * x
}

// %% [markdown]
// # Examples
//
// ## Example A: $x = 3$

// %%
var x = flag.Float64("x", 0.0, "Value of x")

func example() {
  fmt.Printf("Square(%g)=%g\n", *x, Square(*x))
}
// %main example -x=3

// %% [markdown]
// ## Example B: $x = 4$

// %%
// %main example -x=4
""",
):
    nb = jupytext.reads(go, "go")
    for cell in nb.cells:
        assert "gonb" not in cell.source, cell.source

    go2 = jupytext.writes(nb, "go")
    compare(go2, go)


def test_commented_magic(
    go="""// %%
// This is a commented magic
// //gonb:%%

// %% [markdown]
// This is a commented magic in a markdown cell
// // //gonb:%%
""",
):
    nb = jupytext.reads(go, "go")
    assert len(nb.cells) == 2
    assert nb.cells[0].cell_type == "code"
    assert (
        nb.cells[0].source
        == """// This is a commented magic
// %%"""
    )
    assert nb.cells[1].cell_type == "markdown"
    assert (
        nb.cells[1].source
        == """This is a commented magic in a markdown cell
// %%"""
    )
    go2 = jupytext.writes(nb, "go")
    compare(go2, go)


def test_magic_commands_are_commented(
    go="""// %%
// !*rm -f go.work && go work init && go work use . ${HOME}/Projects/gopjrt
// %goworkfix
// %env LD_LIBRARY_PATH=/usr/local/lib
""",
):
    nb = jupytext.reads(go, "go:percent")
    assert len(nb.cells) == 1
    assert nb.cells[0].cell_type == "code"
    assert (
        nb.cells[0].source
        == """!*rm -f go.work && go work init && go work use . ${HOME}/Projects/gopjrt
%goworkfix
%env LD_LIBRARY_PATH=/usr/local/lib"""
    )

    go2 = jupytext.writes(nb, "go")
    compare(go2, go)
