from os import path
from io import open
from setuptools import setup, find_packages

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='jupytext',
    version='0.7.3',
    author='Marc Wouts',
    author_email='marc.wouts@gmail.com',
    description='Jupyter notebooks as Markdown documents, '
                'Julia, Python or R scripts',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/mwouts/jupytext',
    packages=find_packages(),
    entry_points={'console_scripts': ['jupytext = jupytext.cli:jupytext']},
    tests_require=['pytest'],
    install_requires=['nbformat>=4.0.0', 'mock', 'pyyaml', 'testfixtures'],
    license='MIT',
    classifiers=('Development Status :: 4 - Beta',
                 'Environment :: Console',
                 'Framework :: Jupyter',
                 'Intended Audience :: Science/Research',
                 'Programming Language :: Python',
                 'Topic :: Text Processing :: Markup',
                 'Programming Language :: Python',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3',
                 'Programming Language :: Python :: 3.4',
                 'Programming Language :: Python :: 3.5',
                 'Programming Language :: Python :: 3.6',
                 'Programming Language :: Python :: 3.7')
)
