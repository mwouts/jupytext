import shutil, os
from pathlib import Path
try:
    shutil.rmtree('work_dir')
except:
    pass
Path("work_dir/test_dir/python").mkdir(parents=True)
Path("work_dir/python").mkdir(parents=True)
