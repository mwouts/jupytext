-- ---
-- jupyter:
--   kernelspec:
--     display_name: Haskell
--     language: haskell
--     name: haskell
-- ---

-- %% [markdown]
-- # Example Haskell Notebook

-- %% [markdown]
-- Define a function to add two numbers.

-- %%
f :: Num a => a -> a -> a
f x y = x + y

-- %% [markdown]
-- Try to use the function

-- %%
f 1 2 
