from io import open

from setuptools import find_packages, setup

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
    long_description=open("README.md").read(),
    install_requires="""
    termcolor
    click>=8.0.0
    requests
    pygments
    """.split(
        "\n"
    ),
    tests_require=["coverage", "pytest"],
    python_requires=">=3.7",
    packages=find_packages("src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD 3-Clause",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
    entry_points={"console_scripts": ["cromshell-alpha=cromshell.__main__:main_entry"]},
    include_package_data=True,
)
