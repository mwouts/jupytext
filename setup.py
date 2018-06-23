from setuptools import setup, find_packages
from nbrmd.nbrmd import readme

setup(
    name='nbrmd',
    version='0.2.1',
    author='Marc Wouts',
    author_email='marc.wouts@gmail.com',
    description='Jupyter from/to R markdown notebooks',
    long_description=readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/mwouts/nbrmd',
    packages=find_packages(),
    entry_points={'console_scripts': ['nbrmd = nbrmd.cli:main']},
    tests_require=['pytest'],
    license='MIT',
    classifiers=('Development Status :: 3 - Alpha',
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
                 'Programming Language :: Python :: 3.6')
)
