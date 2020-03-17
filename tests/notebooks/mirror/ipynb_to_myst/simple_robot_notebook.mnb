---
kernelspec:
  display_name: Robot Framework
  language: robotframework
  name: robotkernel
---

```{code-cell} robotframework
*** Settings ***

Library  Collections
```

```{code-cell} robotframework
*** Keywords ***

Head
    [Arguments]  ${list}
    ${value}=  Get from list  ${list}  0
    [Return]  ${value}
```

```{code-cell} robotframework
*** Tasks ***

Get head
    ${array}=  Create list  1  2  3  4  5
    ${head}=  Head  ${array}
    Should be equal  ${head}  1
```
