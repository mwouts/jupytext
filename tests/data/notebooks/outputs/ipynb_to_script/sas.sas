/* --- */
/* jupyter: */
/*   kernelspec: */
/*     display_name: SAS */
/*     language: sas */
/*     name: sas */
/* --- */

/* # SAS Notebooks with jupytext */

proc sql;
    select *
    from sashelp.cars (obs=10)
    ;
quit; 

%let name = "Jupytext";

%put &name;

/* +
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
