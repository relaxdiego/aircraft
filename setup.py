# Always place your charm's dependencies here and not directly in requirements.txt.
# This ensures that when `make dependencies` runs, it will install the runtime
# dependencies correctly. In addition, `make dependencies` will take care of
# updating and pinning the runtime dependencies in requirements.txt so that you
# don't have to. For more info, please see "Adding A Runtime Dependency" in this
# project's README.md file
runtime_requirements = [
    'kubernetes'
]

from setuptools import setup

setup(
    install_requires=runtime_requirements,
    version='0.1.0',
    name='charm-dist',
    author='Mark S. Maglana',
    author_email='mmaglana@gmail.com',
    url='https://github.com/relaxdiego/unboxed',
    python_requires='~=3.7',
    package_dir={'': 'src'},
    packages=[
        'charm',
        'unboxed'
    ],

    # https://pypi.org/classifiers/
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX :: Linux",
    ]
)
