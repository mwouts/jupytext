// ---
// jupyter:
//   kernelspec:
//     display_name: .NET (F#)
//     language: F#
//     name: .net-fsharp
// ---

// %% [markdown]
// This notebook was inspired by [Plottting with XPlot](https://github.com/dotnet/interactive/blob/master/NotebookExamples/fsharp/Docs/Plotting%20with%20Xplot.ipynb).

// %%
open XPlot.Plotly

// %%
let bar =
    Bar(
        name = "Bar 1",
        x = ["A"; "B"; "C"],
        y = [1; 3; 2])

[bar]
|> Chart.Plot
|> Chart.WithTitle "A sample bar plot"
