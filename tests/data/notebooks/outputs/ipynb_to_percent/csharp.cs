// ---
// jupyter:
//   kernelspec:
//     display_name: .NET (C#)
//     language: C#
//     name: .net-csharp
// ---

// %% [markdown]
// We start with...

// %%
Console.WriteLine("Hello World!");

// %% [markdown]
// Then we do a plot with Plotly, following the [Plotting with XPlot](https://github.com/dotnet/interactive/blob/master/NotebookExamples/csharp/Docs/Plotting%20with%20Xplot.ipynb) example from `dotnet/interactive`:

// %%
using XPlot.Plotly;

var bar = new Graph.Bar
{
    name = "Bar",
    x = new[] {'A', 'B', 'C'},
    y = new[] {1, 3, 2}
};

var chart = Chart.Plot(new[] {bar});
chart.WithTitle("A bar plot");
display(chart);

// %% [markdown]
// We also test the math outputs as in the [Math and Latex](https://github.com/dotnet/interactive/blob/master/NotebookExamples/csharp/Docs/Math%20and%20LaTeX.ipynb) example:

// %%
(LaTeXString)@"\begin{align} e^{i \pi} = -1\end{align}"

// %%
(MathString)@"e^{i \pi} = -1"
