import jupytext


def test_jupytext_same_as_knitr_spin(r_spin_file, tmpdir):
    nb = jupytext.read(r_spin_file)
    rmd_jupytext = jupytext.writes(nb, "Rmd")

    # Rmd file generated with spin(hair='R/spin.R', knit=FALSE)
    rmd_file = r_spin_file.replace("R_spin", "Rmd").replace(".R", ".Rmd")

    with open(rmd_file) as fp:
        rmd_spin = fp.read()

    assert rmd_spin == rmd_jupytext
