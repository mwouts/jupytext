---
kernelspec:
  display_name: Javascript (Node.js)
  language: javascript
  name: javascript
---

## A notebook that uses IJavascript kernel

```{code-cell}
let x = 5;
const y = 6;
var z = 10;
```

```{code-cell}
x + y;
```

```{code-cell}
function add(num1, num2) {
    return num1 + num2
}
```

```{code-cell}
add(x, y);
```

```{code-cell}
const arrowAdd = (num1, num2) => num1 + num2;
```

```{code-cell}
arrowAdd(x, y);
```

```{code-cell}
const myCar = {
    color: "blue",
    weight: 850,
    model: "fiat",
    start: () => "car started!",
    doors: [1,2,3,4]
}
```

```{code-cell}
console.log("color:", myCar.color);
```

```{code-cell}
console.log("start:", myCar.start());
```

```{code-cell}
for (let door of myCar.doors) {
    console.log("I'm door", door)
}
```

```{code-cell}
myCar;
```

```{code-cell}
class User {
  constructor(name){
    this.name = name;
  }
  sayHello(){
    return "Hello, I'm " + this.name;
  }
}
```

```{code-cell}
let John = new User("John");
John.sayHello();
```
