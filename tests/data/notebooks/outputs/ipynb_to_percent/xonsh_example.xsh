# ---
# jupyter:
#   kernelspec:
#     display_name: Xonsh
#     language: xonsh
#     name: xonsh
# ---

# %%
len($(curl -L https://xon.sh))

# %%
for filename in `.*`:
    print(filename)
    du -sh @(filename)
