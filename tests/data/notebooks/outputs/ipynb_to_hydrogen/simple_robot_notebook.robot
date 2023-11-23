# ---
# jupyter:
#   kernelspec:
#     display_name: Robot Framework
#     language: robotframework
#     name: robotkernel
# ---

# %%
*** Settings ***

Library  Collections

# %%
*** Keywords ***

Head
    [Arguments]  ${list}
    ${value}=  Get from list  ${list}  0
    [Return]  ${value}

# %%
*** Tasks ***

Get head
    ${array}=  Create list  1  2  3  4  5
    ${head}=  Head  ${array}
    Should be equal  ${head}  1
