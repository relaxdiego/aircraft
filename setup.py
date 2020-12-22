# Always place your charm's dependencies here and not directly in requirements.txt.
# This ensures that when `make dependencies` runs, it will install the runtime
# dependencies correctly. In addition, `make dependencies` will take care of
# updating and pinning the runtime dependencies in requirements.txt so that you
# don't have to. For more info, please see "Adding A Runtime Dependency" in this
# project's README.md file
runtime_requirements = [
    "click~=7.0",
    "privy~=6.0",
    "pydantic~=1.6",
    "pyinfra~=1.2",
    "pyyaml~=5.0",
]

import pathlib
from setuptools import (
    find_packages,
    setup,
)

# Some options here are taken from this handy guide:
# https://realpython.com/pypi-publish-python-package/

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

setup(
    install_requires=runtime_requirements,
    version='0.4.0',  # DO NOT EDIT DIRECTLY! Use `bumpversion major|minor|patch`
    name='aircraft',
    author='Mark S. Maglana',
    author_email='mmaglana@gmail.com',
    long_description=README,
    long_description_content_type="text/markdown",
    url='https://github.com/relaxdiego/aircraft',
    python_requires='~=3.6',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    entry_points={
        'console_scripts': [
            'aircraft = aircraft.cli.main:main'
        ],
    },

    # https://pypi.org/classifiers/
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX :: Linux",
    ]
)
