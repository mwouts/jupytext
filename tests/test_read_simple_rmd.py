import re
from testfixtures import compare
import nbrmd


def test_read_mostly_py_rmd_file(rmd="""# ---
# title: Simple file
# ---

```{python, echo=TRUE}
x = np.arange(0, 2*math.pi, eps)
```

```{python, echo=TRUE}
x = np.arange(0,1,eps)
y = np.abs(x)-.5
```

```{r}
ls()
```

```{r, results='asis'}
cat(stringi::stri_rand_lipsum(3), sep='\n\n')
```
"""):
    nb = nbrmd.reads(rmd, ext='.Rmd')
    assert nb.metadata == {'main_language': 'python'}
    assert nb.cells == [{'cell_type': 'markdown',
                         'source': '# ---\n# title: Simple file\n# ---',
                         'metadata': {}},
                        {'cell_type': 'code',
                         'metadata': {'hide_input': False},
                         'execution_count': None,
                         'source': 'x = np.arange(0, 2*math.pi, eps)',
                         'outputs': []},
                        {'cell_type': 'code',
                         'metadata': {'hide_input': False},
                         'execution_count': None,
                         'source': 'x = np.arange(0,1,eps)\ny = np.abs(x)-.5',
                         'outputs': []},
                        {'cell_type': 'code',
                         'metadata': {},
                         'execution_count': None,
                         'source': '%%R\nls()',
                         'outputs': []},
                        {'cell_type': 'code',
                         'metadata': {'results': "'asis'"},
                         'execution_count': None,
                         'source': "%%R\ncat(stringi::"
                                   "stri_rand_lipsum(3), sep='\n\n')",
                         'outputs': []}]

    rmd2 = nbrmd.writes(nb, ext='.Rmd')
    rmd2 = re.sub(r'```{r ', '```{r, ', rmd2)
    rmd2 = re.sub(r'```{python ', '```{python, ', rmd2)
    compare(rmd, rmd2)
