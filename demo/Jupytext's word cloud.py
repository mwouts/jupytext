# This is a notebook that I used to generate Jupytext's word cloud.
# To open this script as a notebook in JupyterLab, right-click on this file, and select _Open with/Notebook_.

from wordcloud import WordCloud

text = """
Jupytext
Notebook
JupyterLab
Git
GitHub
Version control
Markdown
R Markdown
Text
Scripts
Code
Notebook Template
Binder
Visual Studio Code
PyCharm
Atom
Spyder
Hydrogen
RStudio
Sphinx-Gallery
Documentation
black
pytest
autopep8
Metadata
Reproducible research
R
Julia
Python
Bash
Powershell
Scala
Scheme
Clojure
Matlab
Octave
C++
q/kdb+
IDL
TypeScript
Javascript
Scala
Rust
Robot Framework
"""

wordcloud = WordCloud(
    random_state=1,
    background_color='white',
    width=1200, height=500
).generate_from_frequencies({word: 1 for word in text.splitlines()})

wordcloud.to_image()

wordcloud.to_file('../docs/jupytext_word_cloud.png')
