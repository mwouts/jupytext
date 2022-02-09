import jupytext
from jupytext.compare import compare


def test_read_simple_file(
    script=""";; ---
;; title: Simple file
;; ---

;; Here we have some text
;; And below we have some code

(define a 35)
""",
):
    for file_extension in ("ss", "scm"):
        nb = jupytext.reads(script, file_extension)
        assert len(nb.cells) == 3
        assert nb.cells[0].cell_type == "raw"
        assert nb.cells[0].source == "---\ntitle: Simple file\n---"
        assert nb.cells[1].cell_type == "markdown"
        assert (
            nb.cells[1].source == "Here we have some text\n"
            "And below we have some code"
        )
        assert nb.cells[2].cell_type == "code"
        compare(nb.cells[2].source, "(define a 35)")

        script2 = jupytext.writes(nb, file_extension)
        compare(script2, script)
