# -*- coding: utf-8 -*-

from jupytext.compare import compare
import jupytext


def test_read_simple_file(
    script=""";; ---
;; title: Simple file
;; ---

;; Here we have some text
;; And below we have some code

((fn
  []
  (println "Hello World")))
""",
):
    nb = jupytext.reads(script, "clj")
    assert len(nb.cells) == 3
    assert nb.cells[0].cell_type == "raw"
    assert nb.cells[0].source == "---\ntitle: Simple file\n---"
    assert nb.cells[1].cell_type == "markdown"
    assert (
        nb.cells[1].source == "Here we have some text\n" "And below we have some code"
    )
    assert nb.cells[2].cell_type == "code"
    compare(
        nb.cells[2].source,
        """((fn
  []
  (println "Hello World")))""",
    )

    script2 = jupytext.writes(nb, "clj")
    compare(script2, script)
