.DEFAULT_GOAL := help

##
## Available Goals:
##


## build          : Builds the package in preparation for publishing
##                  to PyPI.
##
.PHONY: build
build: .last-build

.last-build: src/* .last-pip-sync
	@rm -rf dist
	@(python setup.py sdist || echo "build error") | tee .last-build
	@(twine check dist/* || echo "build error") | tee -a .last-build
	@(grep "build error" .last-build 1>/dev/null 2>&1 && rm -f .last-build && exit 1) || true


## clean          : Uninstalls all dependencies and removes build and
##                  test artifacts.
##
.PHONY: clean
clean:
	@pip uninstall -y -r requirements.txt -r requirements-dev.txt 2>/dev/null || true
	@pip uninstall -y pip-tools 2>/dev/null || true
	@rm -fv .last* .coverage ${requirements}
	@rm -rfv build/ *.egg-info **/__pycache__ .pytest_cache .tox htmlcov


## coverage-server: Launches an HTTP server on http://localhost:5000
##                  that serves live test coverage reports.
##
.PHONY: coverage-server
coverage-server:
	@cd htmlcov && python3 -m http.server 5000


## dependenceis   : Ensures pip-tools is installed and then ensures
##                  the right dependency versions are installed.
##
.PHONY: dependencies
dependencies: .last-pip-tools-install .last-pip-sync

.last-pip-sync: requirements-dev.txt requirements.txt
	@(pip-sync requirements-dev.txt requirements.txt || echo "pip-sync error") | tee .last-pip-sync
	@(grep "pip-sync error" .last-pip-sync 1>/dev/null 2>&1 && rm -f .last-pip-sync && exit 1) || true
	@pyenv rehash

.last-pip-tools-install:
	@(pip-compile --version 1>/dev/null 2>&1 || pip --disable-pip-version-check install "pip-tools>=5.3.0,<5.4" || echo "pip-tools install error") | tee .last-pip-tools-install
	@(grep "pip-tools install error" .last-pip-tools-install 1>/dev/null 2>&1 && rm -f .last-pip-tools-install && exit 1) || true

requirements.txt: setup.py
	@CUSTOM_COMPILE_COMMAND="make dependencies" pip-compile

requirements-dev.txt: requirements-dev.in requirements.txt
	@CUSTOM_COMPILE_COMMAND="make dependencies" pip-compile  requirements-dev.in


## publish        : Publishes the latest build (or creates one if the
##                  the last one is stale) and then publishes it to PyPI.
##                  It will also tag the current HEAD accordingly. It will
##                  then instruct you on how to bump the project's verions.
##                  Note that once a version has been published, you will
##                  no longer be able to overwrite or modify it even if you
##                  delete the version.
##
.PHONY: publish
publish: .last-publish

CURRENT_VERSION=$(shell grep current_version .bumpversion.cfg | sed -r s,'^.*= ?',,)
CURRENT_HEAD=$(shell git rev-parse --short HEAD)

.last-publish: .last-build
	@(twine upload dist/* || echo "publish error") | tee .last-publish
	@(grep "publish error" .last-publish 1>/dev/null 2>&1 && rm -f .last-publish && exit 1) || true
	@git tag -a -s v$(CURRENT_VERSION) $(CURRENT_HEAD) -m "Tag $(CURRENT_VERSION)" || exit 1
	@(echo "Please prepare the next release by running: bumpversion major|minor|patch")


## test           : Runs the tests
##
.PHONY: test
test: .last-pip-sync .last-pip-tools-install
	pytest --capture=no -vv
	

# From: https://swcarpentry.github.io/make-novice/08-self-doc/index.html
## help           : Print this help message
##
.PHONY : help
help : Makefile
	@sed -n 's/^##//p' $<
