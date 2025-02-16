---
kernelspec:
  display_name: Bash
  language: bash
  name: bash
language_info:
  codemirror_mode: shell
  file_extension: .sh
  mimetype: text/x-sh
  name: bash
---

```{code-cell}
ls
```

```{code-cell}
# https://coderwall.com/p/euwpig/a-better-git-log
git config --global alias.lg "log --color --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset' --abbrev-commit"
```

```{code-cell}
git lg
```
