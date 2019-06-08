---
jupyter:
  kernelspec:
    display_name: 'Javascript (Node.js)'
    language: javascript
    name: javascript
  nbformat: 4
  nbformat_minor: 2
---

::: {.cell .markdown}
## A notebook that uses IJavascript kernel
:::

::: {.cell .code}
``` {.javascript}
let x = 5;
const y = 6;
var z = 10;
```
:::

::: {.cell .code}
``` {.javascript}
x + y;
```
:::

::: {.cell .code}
``` {.javascript}
function add(num1, num2) {
    return num1 + num2
}
```
:::

::: {.cell .code}
``` {.javascript}
add(x, y);
```
:::

::: {.cell .code}
``` {.javascript}
const arrowAdd = (num1, num2) => num1 + num2;
```
:::

::: {.cell .code}
``` {.javascript}
arrowAdd(x, y);
```
:::

::: {.cell .code}
``` {.javascript}
const myCar = {
    color: "blue",
    weight: 850,
    model: "fiat",
    start: () => "car started!",
    doors: [1,2,3,4]
}
```
:::

::: {.cell .code}
``` {.javascript}
console.log("color:", myCar.color);
```
:::

::: {.cell .code}
``` {.javascript}
console.log("start:", myCar.start());
```
:::

::: {.cell .code}
``` {.javascript}
for (let door of myCar.doors) {
    console.log("I'm door", door)
}
```
:::

::: {.cell .code}
``` {.javascript}
myCar;
```
:::

::: {.cell .code}
``` {.javascript}
class User {
  constructor(name){
    this.name = name;
  }
  sayHello(){
    return "Hello, I'm " + this.name;
  }
}
```
:::

::: {.cell .code}
``` {.javascript}
let John = new User("John");
John.sayHello();
```
:::
