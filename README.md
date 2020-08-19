# Juju Charms, Unboxed!

This project serves as my learning journal for [Juju Charms](https://jaas.ai/how-it-works)
in general.

In this repo, I make attempts to dive into the internals of a how a charm
is deployed and handled by Juju so I have to get rid of as much of the
guard rails as possible. That is, I have to "unbox" Juju Charms.

If that doesn't sound like your cup of tea and would much rather get actual
sh\*\* done, then may I suggest that you start with the
[Operator Framework](github.com/canonical/operator) as well as the
[charmcraft](https://github.com/canonical/charmcraft) tool.

I should also note that this project does currently use the
[charmcraft](https://github.com/canonical/charmcraft) tool since I'm currently
more interested examining Juju Charms at runtime rather than
at build time. For more information on how I use it, check out the `Makefile`
in this repo, specifically the `build` goal.

Please note that while I'm an employee of [Canonical](https://canonical.com),
the work that I do in this repo represent my own personal journey. Any opinionated-ness
that you observe here, real or imagined, do not necessarily represent the
views of [Canonical](https://canonical.com/) unless explicitely stated.


## 4-minute Demo

[Watch it on YouTube](https://youtu.be/iwmjgEqEQxY)


## First Make Sure You've Got a Juju model on k8s Running

```
which microk8s && sudo snap remove microk8s
which juju && sudo snap remove juju
sudo snap install --channel=2.8/stable juju --classic
sudo snap install --channel=1.18/stable microk8s --classic
sudo microk8s.enable dns dashboard registry storage metrics-server ingress
sudo snap install --channel=1.18/stable kubectl --classic
mkdir -p ~/.kube
sudo microk8s.config > ~/.kube/config
juju add-k8s k8s-1.18
juju bootstrap k8s-1.18 juju-2-8-1
juju add-model demo
```

You may want to set the unit logging to TRACE so that you can get to the
bottom of any charm errors quickly:

```
juju model-config logging-config="<root>=DEBUG;<unit>=TRACE"
```


## Now Let's Rock and Roll!

Build, and deploy the charm:

```
make build && juju deploy ./unboxed.charm
```

Optionally set the Juju log level to DEBUG:

```
juju model-config logging-config="<root>=WARNING;unit=DEBUG"
```


# Developer's Guide

## Prepare Your Python Environment (venv style)

Create your virtual environment:

```
python3 -m venv ./venv
```

Activate it in every shell session where you intend to run make or
the unit tests (well, when they start to exist 😅)

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
export charm_name=unboxed
pyenv virtualenv 3.7.7 ${charm_name}-3.7.7
```

Your newly created virtualenv should now be automatically activated if your
prompt changed to the following:

```
(unboxed-3.7.7) ubuntu@dev...
```

or, should you happen to be using [dotfiles.relaxdiego.com](https://dotfiles.relaxdiego.com),
if it changed tothe following

```
... via 🐍 v3.7.7 (unboxed-3.7.7)
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


2. Commit `setup.py` and `requirements.txt`. Both
   files should now be updated and the `foo` package installed in your
   local machine. Make sure to commit both files to the repo to let your
   teammates know of the new dependency.

```
git add requirements.txt
git add setup.py
git commit -m "Add bar to requirements.txt"
git push origin
```


## Testing and Building the Charm

After any change in the charm code, you want to ensure that all unit tests
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

More often than not your charm needs to support more than one version of
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
