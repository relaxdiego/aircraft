.PHONY: build changes clean coverage-server dependencies
.DEFAULT_GOAL := .last-build

charm_name := $(shell grep -Eo "^name: *[\"']([A-Za-z0-9\-]*)[\"']" metadata.yaml | sed -E 's/^name: *[\"'\'']([A-Za-z0-9\-]*)[\"'\'']/\1/g')

# WARNING: Use the all argument  only while developing the template, not when developing charms
ifndef all
	requirements=""
else
	requirements=requirements*.txt
endif

# PHONY GOALS

build: .last-build

customized:
	@grep --exclude=Makefile \
		  --exclude=.last-* \
		  --exclude=*requirements.txt \
		  --exclude-dir=.git \
		  --exclude-dir=*.egg-info \
		  --exclude-dir=htmlcov \
		  --exclude-dir=.pytest_cache \
		  --exclude-dir=.tox \
		  --exclude-dir=__pycache__ \
		  --color -n -i -r \
		  changeme . || \
		echo "\nLooks like we're good, champ. Good job changing those changemes!\n"

clean:
	@pip uninstall -y -r requirements.txt -r requirements-dev.txt 2>/dev/null || echo -n
	@pip uninstall -y pip-tools 2>/dev/null || echo -n
	@rm -fv .last* *.charm .coverage ${requirements}
	@rm -rfv build/ *.egg-info **/__pycache__ .pytest_cache .tox htmlcov

coverage-server:
	@cd htmlcov && python3 -m http.server 5000

dependencies: .last-pip-sync .last-pip-tools-install

test: .last-pip-sync .last-pip-tools-install
	pytest --capture=no -vv

# REAL GOALS

.last-pip-sync: requirements-dev.txt requirements.txt
	@pip-sync requirements-dev.txt requirements.txt | tee .last-pip-sync
	@pyenv rehash

.last-build: unboxed/* .last-pip-sync metadata.yaml config.yaml
	@echo "Rebuilding charm '${charm_name}' using 'charmcraft build'"
	@(python -m charmcraft build -e unboxed/charm.py 2>&1 || echo "charmcraft build error") | tee .last-build
	@(grep "charmcraft build error" .last-build 1>/dev/null 2>&1 && rm -f .last-build && exit 1) || true

.last-pip-tools-install:
	@(pip-compile --version 1>/dev/null 2>&1 || pip --disable-pip-version-check install "pip-tools>=5.2.1,<5.3") | tee .last-pip-tools-install

requirements.txt: .last-pip-tools-install setup.py
	@CUSTOM_COMPILE_COMMAND="make dependencies" pip-compile

requirements-dev.txt: .last-pip-tools-install requirements-dev.in requirements.txt
	@CUSTOM_COMPILE_COMMAND="make dependencies" pip-compile  requirements-dev.in
