# AirCraft Library

This is extracted from my [learning journal on Juju Charms](https://github.com/relaxdiego/unboxed)


## Build the Library

```
make build
```


# Developer's Guide

## Prepare Your Python Environment (venv style)

Create your virtual environment:

```
python3 -m venv ./venv
```

Activate it in every shell session where you intend to run make or
the unit tests

```
source ./venv/bin/activate
```

## Prepare Your Python Environment (pyenv style)

You should already have `pyenv` and `pyenv-virtualenv` installed

1. Install Python 3.5, 3.6 and 3.7

```
pyenv install 3.7.7
```

NOTE: For more available versions, run `pyenv install --list`

2. Create a virtualenv for this project

```
pyenv virtualenv 3.7.7 aircraft-3.7.7
```

Your newly created virtualenv should now be automatically activated if your
prompt changed to the following:

```
(aircraft-3.7.7) ubuntu@dev...
```

or, should you happen to be using [dotfiles.relaxdiego.com](https://dotfiles.relaxdiego.com),
if it changed to the following

```
... via 🐍 v3.7.7 (aircraft-3.7.7)
```

Notice the things in parentheses that corresponds to the virtualenv you created
in the previous step. This is thanks to the coordination of pyenv-virtualenv and
the `.python-version` file in the rootdir of this project.

If you `cd ..` or `cd` anywhere else outside your project directory, the virtualenv
will automatically be deactivated. When you `cd` back into the project dir, the
virtualenv will automatically be activated.


## Install The Dependencies

Install all development and runtime dependencies.

WARNING: Make sure you are using a virtualenv before running this command. Since it
         uses pip-sync to install dependencies, it will remove any package that is not
         listed in either `requirements-dev.in` or `setup.py`. If you followed the steps
         in any of the Prepare Your Development Environment sections above, then you
         should be in good shape.

```
make dependencies
```


## Adding A Development Dependency

1. Add it to `requirements-dev.in` and then run make:

```
echo "foo" >> requirements-dev.in
make dependencies
```

This will create `requirements-dev.txt` and then install all dependencies


2. Commit `requirements-dev.in` and `requirements-dev.txt`. Both
   files should now be updated and the `foo` package installed in your
   local machine. Make sure to commit both files to the repo to let your
   teammates know of the new dependency.

```
git add requirements-dev.*
git commit -m "Add foo to requirements-dev.txt"
git push origin
```


## Adding A Runtime Dependency

1. Add it to `runtime_requirements` list in setup.py and then run:

```
make dependencies
```

This will create `requirements.txt` and then install all dependencies


2. Commit `setup.py` and ignore `requirements.txt`. We ignore the latter
   since this is a library project which may be used with different versions
   of its dependencues at development and run time.

```
git add setup.py
git commit -m "Add bar to requirements"
git push origin
```


## Testing and Building the Charm

After any change in the library, you want to ensure that all unit tests
pass before building it. This can be easily done by running:

```
make test build
```


## Viewing the Coverage Report

To view the coverage report, run the tests first and then run:

```
make coverage-server
```

This will run a simple web server on port 5000 that will serve the files
in the auto-generated `htmlcov/` directory. You may leave this server running
in a separate session as you run the tests so that you can just switch back
to the browser and hit refresh to see the changes to your coverage down to
the line of code.


## Running the Tests in Multiple Python Versions

More often than not you want to be able to support more than one version of
Python. This is where tox comes in. Just run the following to get test
results for all Python versions listed in tox.ini's envlist config option

```
tox
```

## Need A Fresh Start?

Sigh, oh what we'd give to get a fresh start in life, huh? Oh, wait, you
mean just the project directory's state? Oh, well we got you covered there
too! Just run:

```
make clean
```

## Really Clean Everything

If you want to remove *everything* that make created including the compiled
`requirements*.txt` files, then run the following:

```
make clean all=t
```
