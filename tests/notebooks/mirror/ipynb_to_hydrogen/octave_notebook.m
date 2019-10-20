% ---
% jupyter:
%   kernelspec:
%     display_name: Octave
%     language: octave
%     name: octave
% ---

% %% [markdown]
% A markdown cell

% %%
1 + 1

% %%
% a code cell with comments
2 + 2

% %%
% a simple plot
x = -10:0.1:10;
plot (x, sin (x));

% %%
%plot -w 800
% a simple plot with a magic instruction
x = -10:0.1:10;
plot (x, sin (x));

% %% [markdown]
% And to finish with, a Python cell

% %%
%%python
a = 1

% %%
%%python
a + 1
