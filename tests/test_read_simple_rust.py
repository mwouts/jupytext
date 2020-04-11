from nbformat.v4.nbbase import new_notebook, new_markdown_cell, new_code_cell
import jupytext
from jupytext.compare import compare, compare_notebooks


def test_read_magics(text="// :vars\n"):
    nb = jupytext.reads(text, "rs")
    compare_notebooks(nb, new_notebook(cells=[new_code_cell(":vars")]))
    compare(jupytext.writes(nb, "rs"), text)


def test_read_simple_file(
    text="""println!("Hello world");
eprintln!("Hello error");
format!("Hello {}", "world")

// A Function
pub fn fib(x: i32) -> i32 {
    if x <= 2 {0} else {fib(x - 2) + fib(x - 1)}
}

// This is a
// Markdown cell

// This is a magic instruction
// :vars

// This is a rust identifier
::std::mem::drop
""",
):
    nb = jupytext.reads(text, "rs")
    compare_notebooks(
        nb,
        new_notebook(
            cells=[
                new_code_cell(
                    """println!("Hello world");
eprintln!("Hello error");
format!("Hello {}", "world")"""
                ),
                new_code_cell(
                    """// A Function
pub fn fib(x: i32) -> i32 {
    if x <= 2 {0} else {fib(x - 2) + fib(x - 1)}
}"""
                ),
                new_markdown_cell("This is a\nMarkdown cell"),
                new_code_cell(
                    """// This is a magic instruction
:vars"""
                ),
                new_code_cell(
                    """// This is a rust identifier
::std::mem::drop"""
                ),
            ]
        ),
    )
    compare(jupytext.writes(nb, "rs"), text)


def test_read_write_script_with_metadata_241(
    no_jupytext_version_number,
    rsnb="""#!/usr/bin/env scriptisto
// ---
// jupyter:
//   jupytext:
//     text_representation:
//       extension: .rs
//       format_name: light
//   kernelspec:
//     display_name: Rust
//     language: rust
//     name: rust
// ---

let mut a: i32 = 2;
a += 1;
""",
):
    nb = jupytext.reads(rsnb, "rs")
    assert "executable" in nb.metadata["jupytext"]
    rsnb2 = jupytext.writes(nb, "rs")

    compare(rsnb, rsnb2)
