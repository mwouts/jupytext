// ---
// jupyter:
//   kernelspec:
//     display_name: Javascript (Node.js)
//     language: javascript
//     name: javascript
// ---

// %% [markdown]
// ## A notebook that uses IJavascript kernel

// %%
let x = 5;
const y = 6;
var z = 10;

// %%
x + y;

// %%
function add(num1, num2) {
    return num1 + num2
}

// %%
add(x, y);

// %%
const arrowAdd = (num1, num2) => num1 + num2;

// %%
arrowAdd(x, y);

// %%
const myCar = {
    color: "blue",
    weight: 850,
    model: "fiat",
    start: () => "car started!",
    doors: [1,2,3,4]
}

// %%
console.log("color:", myCar.color);

// %%
console.log("start:", myCar.start());

// %%
for (let door of myCar.doors) {
    console.log("I'm door", door)
}

// %%
myCar;

// %%
class User {
  constructor(name){
    this.name = name;
  }
  sayHello(){
    return "Hello, I'm " + this.name;
  }
}

// %%
let John = new User("John");
John.sayHello();
