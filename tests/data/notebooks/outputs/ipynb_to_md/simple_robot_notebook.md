---
jupyter:
  kernelspec:
    display_name: Robot Framework
    language: robotframework
    name: robotkernel
---

```robotframework
*** Settings ***

Library  Collections
```

```robotframework
*** Keywords ***

Head
    [Arguments]  ${list}
    ${value}=  Get from list  ${list}  0
    [Return]  ${value}
```

```robotframework
*** Tasks ***

Get head
    ${array}=  Create list  1  2  3  4  5
    ${head}=  Head  ${array}
    Should be equal  ${head}  1
```
