#!/usr/bin/env python

from setuptools import find_packages, setup

with open("requirements.txt") as fh:
    install_requires = fh.readlines()

with open("test-requirements.txt") as fh:
    test_install_requires = fh.readlines()
    test_install_requires.remove("-r requirements.txt")
    test_install_requires.extend(install_requires)

with open("README.md") as fh:
    long_description = fh.read()

# following src dir layout according to
# https://blog.ionelmc.ro/2014/05/25/python-packaging/#the-structure
version = "2.0.0"
setup(
    name="cromshell",
    version=version,
    description="Command Line Interface (CLI) for Cromwell servers",
    author="Jonn Smith, Louis Bergelson, Beri Shifaw",
    author_email="jonn@broadinstitute.org, louisb@broadinstitute.org, "
    "bshifaw@broadinstitute.org",
    license="BSD 3-Clause",
    long_description=long_description,
    install_requires=install_requires,
    tests_require=test_install_requires,
    python_requires=">=3.7",
    packages=find_packages("src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
    entry_points={"console_scripts": ["cromshell-beta=cromshell.__main__:main_entry"]},
    include_package_data=True,
)
