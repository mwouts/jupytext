---
jupyter:
  kernelspec:
    display_name: Javascript (Node.js)
    language: javascript
    name: javascript
---

## A notebook that uses IJavascript kernel

```javascript
let x = 5;
const y = 6;
var z = 10;
```

```javascript
x + y;
```

```javascript
function add(num1, num2) {
    return num1 + num2
}
```

```javascript
add(x, y);
```

```javascript
const arrowAdd = (num1, num2) => num1 + num2;
```

```javascript
arrowAdd(x, y);
```

```javascript
const myCar = {
    color: "blue",
    weight: 850,
    model: "fiat",
    start: () => "car started!",
    doors: [1,2,3,4]
}
```

```javascript
console.log("color:", myCar.color);
```

```javascript
console.log("start:", myCar.start());
```

```javascript
for (let door of myCar.doors) {
    console.log("I'm door", door)
}
```

```javascript
myCar;
```

```javascript
class User {
  constructor(name){
    this.name = name;
  }
  sayHello(){
    return "Hello, I'm " + this.name;
  }
}
```

```javascript
let John = new User("John");
John.sayHello();
```
