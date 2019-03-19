from setuptools import setup, find_packages

setup(
    name="SimpleDeployer",
    version="1.0.0",
    url="",
    license="",
    author="Michael Dombrowski",
    entry_points={"console_scripts": ["simpledeployer=deployer.deployer:main"]},
    install_requires=["gitpython>=2.1.11", "pyyaml>=5.1"],
    packages=find_packages(),
    author_email="",
    description="",
)
