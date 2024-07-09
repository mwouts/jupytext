// -*- coding: utf-8 -*-
// ---
// jupyter:
//   kernelspec:
//     display_name: Go (gonb)
//     language: go
//     name: gonb
// ---

// A notebook that use [GoNB](https://github.com/janpfeifer/gonb)

// the code below comes from [tutorial.ipynb](https://github.com/janpfeifer/gonb/blob/main/examples/tutorial.ipynb)

func main() {
    fmt.Printf("Hello World!")
}

//gonb:%%
fmt.Printf("Hello World!")

// //gonb:%% --who=world can pass flags to main func

// +
import (
    "flag"
    "fmt"
)

var flagWho = flag.String("who", "", "Your name!")

//gonb:%% --who=world
fmt.Printf("Hello %s!\n", *flagWho)
// -

// // %args also can pass flags

// +
// %args --who=Wally

func main() {
    flag.Parse()
    fmt.Printf("Where is %s?", *flagWho)
}

// +
import "github.com/janpfeifer/gonb/gonbui"

//gonb:%%
gonbui.DisplayHtml(`<span style="background:pink; color:#111; border-radius: 3px; border: 3px solid orange; font-size: 18px;">I 🧡 GoNB!</span>`)
// -

//gonb:%%
gonbui.DisplayMarkdown("#### Objective\n\n1. Have fun coding **Go**;\n1. Profit...\n"+
                       `$$f(x) = \int_{-\infty}^{\infty} e^{-x^2} dx$$`)

func init_a() {
    fmt.Println("init_a")
}
//gonb:%%
fmt.Println("main")
