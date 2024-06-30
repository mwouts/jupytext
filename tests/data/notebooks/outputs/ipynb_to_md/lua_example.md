---
jupyter:
  kernelspec:
    display_name: Lua
    language: lua
    name: lua
---

Source: https://www.lua.org/pil/19.3.html


# Sort


Another useful function on arrays is table.sort, which we have seen before. It receives the array to be sorted, plus an optional order function. This order function receives two arguments and must return true if the first argument should come first in the sorted array. If this function is not provided, sort uses the default less-than operation (corresponding to the `<´ operator).


A common mistake is to try to order the indices of a table. In a table, the indices form a set, and have no order whatsoever. If you want to order them, you have to copy them to an array and then sort the array. Let us see an example. Suppose that you read a source file and build a table that gives, for each function name, the line where that function is defined; something like this:

```lua
lines = {
    luaH_set = 10,
    luaH_get = 24,
    luaH_present = 48,
}
```

 Now you want to print these function names in alphabetical order. If you traverse this table with pairs, the names appear in an arbitrary order. However, you cannot sort them directly, because these names are keys of the table. However, when you put these names into an array, then you can sort them. First, you must create an array with those names, then sort it, and finally print the result:

```lua
a = {}
for n in pairs(lines) do table.insert(a, n) end
table.sort(a)
for i,n in ipairs(a) do print(n) end
```

Note that, for Lua, arrays also have no order. But we know how to count, so we get ordered values as long as we access the array with ordered indices. That is why you should always traverse arrays with ipairs, rather than pairs. The first imposes the key order 1, 2, ..., whereas the latter uses the natural arbitrary order of the table.


As a more advanced solution, we can write an iterator that traverses a table following the order of its keys. An optional parameter f allows the specification of an alternative order. It first sorts the keys into an array, and then iterates on the array. At each step, it returns the key and value from the original table:

```lua
function pairsByKeys (t, f)
    local a = {}
    for n in pairs(t) do table.insert(a, n) end
    table.sort(a, f)
    local i = 0               -- iterator variable
    local iter = function ()  -- iterator function
        i = i + 1
        if a[i] == nil then return nil
        else return a[i], t[a[i]]
        end
    end
    return iter
end
```

 With this function, it is easy to print those function names in alphabetical order. The loop

```lua
for name, line in pairsByKeys(lines) do
    print(name, line)
end
```
