from setuptools import setup, find_packages

from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="SimpleDeployer",
    version="1.1.0",
    url="https://github.com/mikedombo/simpledeployer",
    license="BSD-3-Clause",
    author="Michael Dombrowski",
    entry_points={"console_scripts": ["simpledeployer=deployer.deployer:main"]},
    install_requires=["gitpython>=2.1.11", "pyyaml>=5.1", "click>=7.0"],
    packages=find_packages(),
    author_email="michael@mikedombrowski.com",
    description="Dead simple deployment system",
    long_description=long_description,
    long_description_content_type='text/markdown'
)
