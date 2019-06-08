---
jupyter:
  kernelspec:
    display_name: 'Typescript 3.5'
    language: typescript
    name: typescript
  nbformat: 4
  nbformat_minor: 2
---

::: {.cell .code}
``` {.typescript}
let x: number = 5;
const y: number = 6;
var z: string = "hi";
console.log(z);
x + y;
```
:::

::: {.cell .code}
``` {.typescript}
function add(num1: number, num2: number): number {
    return num1 + num2
}
add(x, y);
```
:::

::: {.cell .code}
``` {.typescript}
const arrowAdd = (num1: number, num2: number) => num1 + num2;
arrowAdd(x, y);
```
:::

::: {.cell .code}
``` {.typescript}
class User {
  constructor(private name: string) {
    this.name = name;
  }
  sayHello(): string {
    return "Hello, I'm " + this.name;
  }
}
let John: User;
John = new User("John");
John.sayHello();
```
:::
