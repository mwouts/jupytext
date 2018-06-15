from setuptools import setup

setup(
    name='nbrmd',
    scripts=['nbrmd'],
    version='0.1',
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
)