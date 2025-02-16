---
kernelspec:
  display_name: .NET (F#)
  language: F#
  name: .net-fsharp
language_info:
  file_extension: .fs
  mimetype: text/x-fsharp
  name: C#
  pygments_lexer: fsharp
  version: '4.5'
---

This notebook was inspired by [Plottting with XPlot](https://github.com/dotnet/interactive/blob/master/NotebookExamples/fsharp/Docs/Plotting%20with%20Xplot.ipynb).

```{code-cell} fsharp
open XPlot.Plotly
```

```{code-cell} fsharp
let bar =
    Bar(
        name = "Bar 1",
        x = ["A"; "B"; "C"],
        y = [1; 3; 2])

[bar]
|> Chart.Plot
|> Chart.WithTitle "A sample bar plot"
```
