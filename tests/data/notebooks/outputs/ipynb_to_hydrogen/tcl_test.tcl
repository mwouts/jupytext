# ---
# jupyter:
#   kernelspec:
#     display_name: Tcl
#     language: tcl
#     name: tcljupyter
# ---

# %% [markdown]
# # Assign Values

# %%
set a 1
puts "a = $a"

# %% [markdown]
# # Loop

# %%
for {set i 0} {$i < 10} {incr i} {
    puts "I inside first loop: $i"
}

# %%
