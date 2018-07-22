import sys
import pytest
import nbrmd
from testfixtures import compare

ACTIVE_ALL = {'.py': """# + {"active": "ipynb,py,R,Rmd"}
# This cell is active in all extensions
""",
              '.Rmd': """```{python active="ipynb,py,R,Rmd"}
# This cell is active in all extensions
```
""",
              '.R': """#+ active="ipynb,py,R,Rmd"
# This cell is active in all extensions
""",
              '.ipynb': {'cell_type': 'code',
                         'source': '# This cell is active in all extensions',
                         'metadata': {'active': 'ipynb,py,R,Rmd'},
                         'execution_count': None,
                         'outputs': []}}


@pytest.mark.parametrize('ext', ['.Rmd', '.py', '.R'])
def test_active_all(ext):
    nb = nbrmd.reads(ACTIVE_ALL[ext], ext=ext)
    assert len(nb.cells) == 1
    compare(nb.cells[0], ACTIVE_ALL['.ipynb'])
    compare(ACTIVE_ALL[ext], nbrmd.writes(nb, ext=ext))


ACTIVE_PY_IPYNB = {'.py': """# + {"active": "ipynb,py"}
# This cell is active in py and ipynb extensions
""",
                   '.Rmd': """```{python active="ipynb,py", eval=FALSE}
# This cell is active in py and ipynb extensions
```
""",
                   '.R': """#' ```{python active="ipynb,py", eval=FALSE}
#' # This cell is active in py and ipynb extensions
#' ```
""",
                   '.ipynb': {'cell_type': 'code',
                              'source': '# This cell is active in py and '
                                        'ipynb extensions',
                              'metadata': {'active': 'ipynb,py'},
                              'execution_count': None,
                              'outputs': []}}


@pytest.mark.skipif(sys.version_info < (3, 6),
                    reason="unordered dict result in changes in chunk options")
@pytest.mark.parametrize('ext', ['.Rmd', '.py'])  # TODO: add R
def test_active_py_ipynb(ext):
    nb = nbrmd.reads(ACTIVE_PY_IPYNB[ext], ext=ext)
    assert len(nb.cells) == 1
    compare(nb.cells[0], ACTIVE_PY_IPYNB['.ipynb'])
    compare(ACTIVE_PY_IPYNB[ext], nbrmd.writes(nb, ext=ext))


ACTIVE_RMD = {'.py': """# # + {"active": "Rmd"}
# # This cell is active in Rmd only
""",
              '.Rmd': """```{python active="Rmd"}
# This cell is active in Rmd only
```
""",
              '.R': """#' ```{python active="Rmd", eval=FALSE}
#' # This cell is active in Rmd only
#' ```
""",
              '.ipynb': {'cell_type': 'raw',
                         'source': '# This cell is active in Rmd only',
                         'metadata': {'active': 'Rmd'}}}


@pytest.mark.parametrize('ext', ['.Rmd'])  # TODO: add R and py
def test_active_rmd(ext):
    nb = nbrmd.reads(ACTIVE_RMD[ext], ext=ext)
    assert len(nb.cells) == 1
    compare(nb.cells[0], ACTIVE_RMD['.ipynb'])
    compare(ACTIVE_RMD[ext], nbrmd.writes(nb, ext=ext))
