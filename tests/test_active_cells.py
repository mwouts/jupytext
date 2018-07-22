import nbrmd
from testfixtures import compare

PY_ACTIVE_ALL = """# + {"active": "ipynb,py,R,rmd"}
# This cell is active in all extensions
"""

RMD_ACTIVE_ALL = """```{python active="ipynb,py,R,rmd"}
# This cell is active in all extensions
```
"""

R_ACTIVE_ALL = """#+ active="ipynb,py,R,rmd"
# This cell is active in all extensions
"""

IPYNB_ACTIVE_ALL = {'cell_type': 'code',
                    'source': '# This cell is active in all extensions',
                    'metadata': {'active': 'ipynb,py,R,rmd'},
                    'execution_count': None,
                    'outputs': []}


def test_active_all_py():
    nb = nbrmd.reads(PY_ACTIVE_ALL, ext='.py')
    assert len(nb.cells) == 1
    compare(nb.cells[0], IPYNB_ACTIVE_ALL)
    compare(PY_ACTIVE_ALL, nbrmd.writes(nb, ext='.py'))


def test_active_all_rmd():
    nb = nbrmd.reads(RMD_ACTIVE_ALL, ext='.Rmd')
    assert len(nb.cells) == 1
    compare(nb.cells[0], IPYNB_ACTIVE_ALL)
    compare(RMD_ACTIVE_ALL, nbrmd.writes(nb, ext='.Rmd'))


def test_active_all_R():
    nb = nbrmd.reads(R_ACTIVE_ALL, ext='.R')
    assert len(nb.cells) == 1
    compare(nb.cells[0], IPYNB_ACTIVE_ALL)
    compare(R_ACTIVE_ALL, nbrmd.writes(nb, ext='.R'))
