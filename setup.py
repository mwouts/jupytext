from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='nbrmd',
    version='0.1',
    author='Marc Wouts',
    description='Jupyter from/to R markdown notebooks',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/mwouts/nbrmd',
    packages=find_packages(),
    scripts=['bin/nbrmd'],
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
    classifiers=('Development Status :: 2 - Pre-Alpha',
                 'Environment :: Console',
                 'Framework :: Jupyter',
                 'Intended Audience :: Science/Research',
                 'Programming Language :: Python',
                 'Topic :: Text Processing :: Markup')
)
