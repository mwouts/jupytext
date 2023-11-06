# ---
# jupyter:
#   kernelspec:
#     display_name: Bash
#     language: bash
#     name: bash
# ---

# %%
ls

# %%
# https://coderwall.com/p/euwpig/a-better-git-log
git config --global alias.lg "log --color --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset' --abbrev-commit"

# %%
git lg
