::: {.cell .code execution_count="1" collapsed="false" inputHidden="false" outputHidden="false" tags="["parameters"]"}
``` {.python}
param = 4
```
:::

::: {.cell .code execution_count="2" collapsed="false" inputHidden="false" outputHidden="false"}
``` {.python}
import pandas as pd
```
:::

::: {.cell .code execution_count="3" collapsed="false" inputHidden="false" outputHidden="false"}
``` {.python}
df = pd.DataFrame({'A': [1, 2], 'B': [3 + param, 4]},
                  index=pd.Index(['x0', 'x1'], name='x'))
df
```

::: {.output .execute_result execution_count="3"}
<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>A</th>
      <th>B</th>
    </tr>
    <tr>
      <th>x</th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>x0</th>
      <td>1</td>
      <td>7</td>
    </tr>
    <tr>
      <th>x1</th>
      <td>2</td>
      <td>4</td>
    </tr>
  </tbody>
</table>
</div>
:::
:::

::: {.cell .code execution_count="5" collapsed="false" inputHidden="false" outputHidden="false"}
``` {.python}
%matplotlib inline
df.plot(kind='bar')
```

::: {.output .execute_result execution_count="5"}
    <matplotlib.axes._subplots.AxesSubplot at 0x1634278f240>
:::

::: {.output .display_data}
![](fb872010711f861ff8155c73446d346df5939c83.png)
:::
:::
