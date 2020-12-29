Aircraft
========

> BUYER BEWARE: This project is still in very early stages. Its architecture
> will drastically change from day to day as I experiment, make mistakes, and
> implement the lessons learned. I also cannot make any guarantees that the
> entire codebase will always work. Bugs abound. Having said that, if you like
> to browse incomplete code and gain an understanding of how a project is
> designed, this might just be the thing for you!


# Video Introduction

* [View on YouTube](https://youtu.be/-wF3zPSiHOk)
* [Configure PXE on a Pi](https://youtu.be/HzXiBUNrDkg)


# Project Rationale

I work with infrastructure. The kind of infrastructure where you have a bunch
of baremetal machines that don't have an OS installed. Where the only access
you have at the onset are their BMC IPs. In that case, I need some sort of
machine provisioning tool that is agentless. Truly agentless, not just Ansible
agentless.

In other situations, I might need to set up a CI/CD cluster. Now if you're like
me, you'd prefer to configure this cluster on top of as thin a technology stack
as possible (read: just bare OSes). The reason for this is because if you want
to deploy your CI/CD cluster on top of the best whiz-bang technology stack,
such as Kubernetes, you have to ensure that you have a CI/CD infrastructure in
place before you do...but that's exactly what's missing and what we're trying
to deploy! Again, what's needed here is an agentless infrastructure automation
tool.

In both situations, I've found Ansible usable for a time. However, after years
of using it, I've come to find it cumbersome. With its supposed-declarative
YAML-based DSL slowly transforming into a turing-complete language. At this point
one wonders why we don't just use an already proper language itself like, oh
I don't know, Python?

This is what brought be to [pyinfra](https://pyinfra.com/). This project builds
on top of pyinfra's good-enough implementation. It is an attempt at replicating
the Ansible project structure that I've been using for years as exemplified in
another project called [relaxdiego/cicd](https://github.com/relaxdiego/cicd).


## Why Didn't You Just Use Terraform?

I have ample experience with Terraform in the past too and I've maintained the
"Terraform for provisioning, Ansible for configuration" dichotomy for some time.
I maintain that stand for this project but have changed it to "Terraform for
provisioning, Aircraft for configuration."


# Usage

This project doesn't add wrappers around pyinfra, so once you get the hang
of [how to use pyinfra](https://docs.pyinfra.com/en/1.x/getting_started.html),
then you can easily move on to some of the stuff I do in the `examples/` dir
of this project.

Once you're comfortable with pyinfra and you start browsing the `examples/`
dir, you'll see that all I'm doing is adding [pyinfra packaged deploys](https://docs.pyinfra.com/en/1.x/api/deploys.html)
that you can use in your operations files. I've also created some [pydantic](https://pydantic-docs.helpmanual.io/)
models that go with the packaged deploys to help with validating inventory
data. Anyway, check out the `examples/` directory before I keep blabbering
for ages.


# Developer's Guide

## Prerequisites

1. [Python 3](https://www.python.org/downloads/)
2. Make


## Prepare Your Python Environment (pyenv style; one-time only)

You will need two additional dependencies for this style:

1. [pyenv](https://github.com/pyenv/pyenv-installer)
2. [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv)

Once the above dependencies are installed, do the following:

1. Install an isolated environment for your preferred Python version.

```
python_version=<YOUR-PREFERRED-PYTHON-VERSION>
pyenv install --enable-shared $python_version
```

NOTE: For more available versions, run `pyenv install --list`

2. Create a virtualenv for this project

```
pyenv virtualenv $python_version aircraft
```

3. Add a `.python-version` file to this project dir

```
cat >.python-version<<EOF
aircrat
$python_version
EOF
```

Your newly created virtualenv should now be automatically activated if your
prompt changed to the following:

```
(aircraft) ubuntu@dev...
```

or, should you happen to be using [dotfiles.relaxdiego.com](https://dotfiles.relaxdiego.com),
if it changed to the following

```
... via 🐍 <YOUR-PREFERRED-PYTHON-VERSION> (aircraft)
```
Notice the things in parentheses that corresponds to the virtualenv you created
in the previous step. This is thanks to the coordination of pyenv-virtualenv and
the `.python-version` file in the rootdir of this project.

If you `cd ..` or `cd` anywhere else outside your project directory, the virtualenv
will automatically be deactivated. When you `cd` back into the project dir, the
virtualenv will automatically be activated.


## Prepare Your Python Environment (venv style)

If you'd rather manage your virtualenv manually, this section is for you.
Create your virtual environment:

```
python3 -m venv ./venv
```

Activate it in every shell session where you intend to run make or
the unit tests

```
source ./venv/bin/activate
```


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


## Other Make Goals

Run `make help` or check out the contents of `Makefile`.


## Running the Tests in Multiple Python Versions

More often than not you want to be able to support more than one version of
Python. This is where tox comes in. Just run the following to get test
results for all Python versions listed in tox.ini's envlist config option

```
tox
```

# References

* [SecureBoot-Compatible UEFI netboot](https://wiki.ubuntu.com/UEFI/SecureBoot/PXE-IPv6)
* [dnsmasq](https://wiki.archlinux.org/index.php/dnsmasq#Configuration)
* [Fully Automated Ubuntu 20.04 Install](https://askubuntu.com/a/1235724)
* [Configuring PXE Network Boot Server on Ubuntu 18.04 LTS](https://linuxhint.com/pxe_boot_ubuntu_server/)
* [Ubuntu Network installation with PXE](https://xinau.ch/notes/ubuntu-network-installation-with-pxe/)
