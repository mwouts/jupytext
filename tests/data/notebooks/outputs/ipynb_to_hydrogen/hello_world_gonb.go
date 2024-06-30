// -*- coding: utf-8 -*-
// ---
// jupyter:
//   kernelspec:
//     display_name: Go (gonb)
//     language: go
//     name: gonb
// ---

// %% [markdown]
// A notebook that use [GoNB](https://github.com/janpfeifer/gonb)

// %% [markdown]
// the code below comes from [tutorial.ipynb](https://github.com/janpfeifer/gonb/blob/main/examples/tutorial.ipynb)

// %%
func main() {
    fmt.Printf("Hello World!")
}

// %%
%%
fmt.Printf("Hello World!")

// %%
import "github.com/janpfeifer/gonb/gonbui"

%%
gonbui.DisplayHtml(`<span style="background:pink; color:#111; border-radius: 3px; border: 3px solid orange; font-size: 18px;">I 🧡 GoNB!</span>`)

// %%
%%
gonbui.DisplayMarkdown("#### Objective\n\n1. Have fun coding **Go**;\n1. Profit...\n"+
                       `$$f(x) = \int_{-\infty}^{\infty} e^{-x^2} dx$$`)

// %%
func init_a() {
    fmt.Println("init_a")
}
%%
fmt.Println("main")
