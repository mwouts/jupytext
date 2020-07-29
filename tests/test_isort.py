from jupytext import reads, writes
from jupytext.cli import pipe_notebook
from jupytext.compare import compare

from .utils import requires_isort


@requires_isort
def test_pipe_into_isort():
    text_org = """# %%
import numpy as np
np.array([1,2,3])

# %%
import pandas as pd
pd.Series([1,2,3])

# %%
# This is a comment on the second import
import pandas as pd
pd.Series([4,5,6])
"""

    text_target = """# %%
import numpy as np
# This is a comment on the second import
import pandas as pd

np.array([1,2,3])

# %%
pd.Series([1,2,3])

# %%
pd.Series([4,5,6])
"""

    nb_org = reads(text_org, fmt="py:percent")
    nb_pipe = pipe_notebook(
        nb_org, 'isort - --treat-comment-as-code "# %%" --float-to-top'
    )
    text_actual = writes(nb_pipe, "py:percent")
    compare(text_actual, text_target)
