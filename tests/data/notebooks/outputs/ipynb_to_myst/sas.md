---
kernelspec:
  display_name: SAS
  language: sas
  name: sas
---

# SAS Notebooks with jupytext

```{code-cell}
proc sql;
    select *
    from sashelp.cars (obs=10)
    ;
quit; 
```

```{code-cell}
%let name = "Jupytext";
```

```{code-cell}
%put &name;
```

```{code-cell}
/* Note when defining macros "%macro" cannot be the first line of text in the cell */
%macro test;
    data temp;
        set sashelp.cars;
        name = "testx";
    run; 
    proc print data = temp (obs=10);
    run; 
%mend test;

%test
```
