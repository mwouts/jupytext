// ---
// jupyter:
//   kernelspec:
//     display_name: Typescript 3.5
//     language: typescript
//     name: typescript
// ---

let x: number = 5;
const y: number = 6;
var z: string = "hi";
console.log(z);
x + y;

function add(num1: number, num2: number): number {
    return num1 + num2
}
add(x, y);

const arrowAdd = (num1: number, num2: number) => num1 + num2;
arrowAdd(x, y);

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
