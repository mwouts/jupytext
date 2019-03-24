import re
from testfixtures import compare
import jupytext
from .utils import skip_if_dict_is_not_ordered


@skip_if_dict_is_not_ordered
def test_read_mostly_py_rmd_file(rmd="""---
title: Simple file
---

```{python, echo=TRUE}
import numpy as np
x = np.arange(0, 2*math.pi, eps)
```

```{python, echo=TRUE}
x = np.arange(0,1,eps)
y = np.abs(x)-.5
```

```{r}
ls()
```

```{r, results='asis', magic_args='-i x'}
cat(stringi::stri_rand_lipsum(3), sep='\n\n')
```
"""):
    nb = jupytext.reads(rmd, 'Rmd')
    assert nb.cells == [{'cell_type': 'raw',
                         'source': '---\ntitle: Simple file\n---',
                         'metadata': {}},
                        {'cell_type': 'code',
                         'metadata': {'hide_input': False},
                         'execution_count': None,
                         'source': 'import numpy as np\n'
                                   'x = np.arange(0, 2*math.pi, eps)',
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
                         'source': "%%R -i x\ncat(stringi::"
                                   "stri_rand_lipsum(3), sep='\n\n')",
                         'outputs': []}]

    rmd2 = jupytext.writes(nb, 'Rmd')
    rmd2 = re.sub(r'```{r ', '```{r, ', rmd2)
    rmd2 = re.sub(r'```{python ', '```{python, ', rmd2)
    compare(rmd, rmd2)
