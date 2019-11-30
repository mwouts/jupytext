---
jupyter:
  kernelspec:
    display_name: Julia 1.1.1
    language: julia
    name: 'julia-1.1'
  nbformat: 4
  nbformat_minor: 1
---

::: {.cell .code}
``` {.julia}
# IJulia rocks! So does Plotly. Check it out

using Plotly
api_key = "" # visit https://plot.ly/api to generate an API username and password
username = ""

Plotly.signin(username, api_key)
```
:::

::: {.cell .code}
``` {.julia}
# Following data taken from http://julialang.org/ frontpage 
benchmarks = ["fib", "parse_int", "quicksort3", "mandel", "pi_sum", "rand_mat_stat", "rand_mat_mul"]
platforms = ["Fortran", "Julia", "Python", "R", "Matlab", "Mathematica", "Javascript", "Go"]

data = {
        platforms[1] => [0.26, 5.03, 1.11, 0.86, 0.80, 0.64, 0.96],
        platforms[2] => [0.91, 1.60, 1.14, 0.85, 1.00, 1.66, 1.01],
        platforms[3] => [30.37, 13.95, 31.98, 14.19, 16.33, 13.52, 3.41 ],
        platforms[4] => [411.36, 59.40, 524.29, 106.97, 15.42, 10.84, 3.98  ],
        platforms[5] => [1992.00, 1463.16, 101.84, 64.58, 1.29, 6.61, 1.10   ],
        platforms[6] => [64.46, 29.54, 35.74, 6.07, 1.32, 4.52, 1.16 ],
        platforms[7] => [2.18, 2.43, 3.51, 3.49, 0.84, 3.28, 14.60],
        platforms[8] => [1.03, 4.79, 1.25, 2.36, 1.41, 8.12, 8.51]
        }

pdata = [ {"x"=>benchmarks,"y"=>data[k],"bardir"=>"h","type"=>"bar","name"=>k} for k = platforms ]

layout = {
          "title"=> "Julia benchmark comparison (smaller is better, C performance = 1.0)",
          "barmode"=> "group",
          "autosize"=> false,
          "width"=> 900,
          "height"=> 900,
          "titlefont"=>
          {
           "family"=> "Open Sans",
           "size"=> 18,
           "color"=> "rgb(84, 39, 143)"
           },
          "margin"=> {"l"=>160, "pad"=>0},
          "xaxis"=> {
                     "title"=> "Benchmark log-time",
                     "type"=> "log"
                     },
          "yaxis"=> {"title"=> "Benchmark Name"}
          }

response = Plotly.plot(pdata,["layout"=>layout])

# Embed in an iframe within IJulia
s = string("<iframe height='750' id='igraph' scrolling='no' seamless='seamless' src='",
            response["url"],
            "/700/700' width='750'></iframe>")
display("text/html", s)
```
:::

::: {.cell .code}
``` {.julia}
# checkout https://plot.ly/api/ for more Julia examples!
# But to show off some other Plotly features:
x = 1:1500
y1 = sin(2*pi*x/1500.) + rand(1500)-0.5
y2 = sin(2*pi*x/1500.)

fish = {"x"=>x,"y"=> y1,
	"type"=>"scatter","mode"=>"markers",
	"marker"=>{"color"=>"rgb(0, 0, 255)","opacity"=>0.5 } }

fit = {"x"=> x,"y"=> y2,
	"type"=>"scatter", "mode"=>"markers", "opacity"=>0.8,
	"marker"=>{"color"=>"rgb(255, 0, 0)"} }

layout = {"autosize"=> false,
    "width"=> 650, "height"=> 550,
    "title"=>"Fish School",
	"xaxis"=>{ "ticks"=> "",
        "gridcolor"=> "white",
        "zerolinecolor"=> "white",    
        "linecolor"=> "white",
        "autorange"=> false,
        "range"=>[0,1500] },
	"yaxis"=>{ "ticks"=> "",
        "gridcolor"=> "white",
        "zerolinecolor"=> "white",
		"linecolor"=> "white",
        "autorange"=> false,
        "range"=>[-2.2,2.2] },
	"plot_bgcolor"=> "rgb(245,245,247)",
    "showlegend"=> false,
    "hovermode"=> "closest"}

response = Plotly.plot([fish, fit],["layout"=>layout])
s = string("<iframe height='750' id='igraph' scrolling='no' seamless='seamless' src='",
            response["url"],
            "/700/700' width='750'></iframe>")
display("text/html", s)
```
:::
