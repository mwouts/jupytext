---
jupyter:
  kernelspec:
    display_name: Go (gonb)
    language: go
    name: gonb
---

A notebook that use [GoNB](https://github.com/janpfeifer/gonb)


the code below comes from [tutorial.ipynb](https://github.com/janpfeifer/gonb/blob/main/examples/tutorial.ipynb)

```go
func main() {
    fmt.Printf("Hello World!")
}
```

```go
%%
fmt.Printf("Hello World!")
```

%% --who=world can pass flags to main func

```go
import (
    "flag"
    "fmt"
)

var flagWho = flag.String("who", "", "Your name!")

%% --who=world
fmt.Printf("Hello %s!\n", *flagWho)
```

%args also can pass flags

```go
%args --who=Wally

func main() {
    flag.Parse()
    fmt.Printf("Where is %s?", *flagWho)
}
```

```go
import "github.com/janpfeifer/gonb/gonbui"

%%
gonbui.DisplayHtml(`<span style="background:pink; color:#111; border-radius: 3px; border: 3px solid orange; font-size: 18px;">I 🧡 GoNB!</span>`)
```

```go
%%
gonbui.DisplayMarkdown("#### Objective\n\n1. Have fun coding **Go**;\n1. Profit...\n"+
                       `$$f(x) = \int_{-\infty}^{\infty} e^{-x^2} dx$$`)
```

```go
func init_a() {
    fmt.Println("init_a")
}
%%
fmt.Println("main")
```
