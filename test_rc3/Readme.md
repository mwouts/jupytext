Problem:  rc3 won't save my ipynb or py file when the ipynb file is in the directory
that jupyter notebook was launched in (work_dir).  Move one folder
down: (work_dir/test_dir) and everything works file.

To reproduce:  See https://goo.gl/wnNLi7 for a screencast of the following steps

1. cd test_rc3

2. python setup_dirs.py

3. cd work_dir

4. jupyter notebook

5. Try to create a notebook in work_dir -- get autosave error

6. In jupyter, descend to test_dir -- no problem





