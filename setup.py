#
# This file is not necessary for building charms but is, instead, just meant to make
# unit testing easier. By maintaining this file and running `make dependencies`, your
# unit tests will now only need to `from src.charm import YourCharmClass` without
# needing to remember to add `sys.path.append('src')` at the top of each test file.
#


# Always place your charm's dependencies here and not directly in requirements.txt.
# This ensures that when `make dependencies` runs, it will install the runtime
# dependencies correctly. In addition, `make dependencies` will take care of
# updating and pinning the runtime dependencies in requirements.txt so that you
# don't have to. For more info, please see "Adding A Runtime Dependency" in this
# project's README.md file
runtime_requirements = [
    'ops',
]

minimum_python_version = (3, 5, 0)

#
# DO NOT CHANGE ANYTHING BELOW
#

from setuptools import find_packages, setup
from sys import version_info


if version_info[:3] < minimum_python_version:
    raise RuntimeError(
        'Unsupported python version {}. Please use {} or newer'.format(
            '.'.join(map(str, version_info[:3])),
            '.'.join(map(str, minimum_python_version)),
        )
    )


setup(
    install_requires=runtime_requirements,
    name='charm',
    packages=find_packages(),
)
