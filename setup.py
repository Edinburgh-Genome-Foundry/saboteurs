import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages

exec(open('saboteurs/version.py').read()) # loads __version__

setup(
    name='saboteurs',
    version=__version__,
    author='Zulko',

    description='Identify agents impairing success accross experiments.',
    long_description=open('pypi-readme.rst').read(),
    license='see LICENSE.txt',
    url='https://github.com/Edinburgh-Genome-Foundry/saboteurs',
    keywords="statistics weakest link DNA part validation",
    packages=find_packages(exclude='docs'),
    include_package_data=True,
    install_requires=["numpy", "pandas", "scipy", "sklearn", "pdf_reports",
                      "matplotlib", "flametree"])
