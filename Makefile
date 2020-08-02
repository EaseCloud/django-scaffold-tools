# Makefile for Django Scaffold Tools
#
# 	GitHb: https://github.com/easecloud/django-scaffold-tools
# 	Author: Alfred Huang <57082212@qq.com> https://github.com/fish-ball
#

SOURCE_GLOB=$(wildcard bin/*.py scaffold/**/*.py tests/**/*.py examples/*.py)

# F811: https://github.com/PyCQA/pyflakes/issues/320#issuecomment-469337000
IGNORE_PEP=E203,E221,E241,E272,E501,F811

# help scripts to find the right place of wechaty module
export PYTHONPATH=./

.PHONY: all
all : clean lint

.PHONY: clean
clean:
	rm -fr dist/* .pytype

.PHONY: lint
lint: pylint pycodestyle flake8 mypy pytype


# disable: TODO list temporay
.PHONY: pylint
pylint:
	pylint \
		--load-plugins pylint_quotes \
		--disable=W0511,R0801,cyclic-import \
		$(SOURCE_GLOB)

.PHONY: pycodestyle
pycodestyle:
	pycodestyle \
		--statistics \
		--count \
		--ignore="${IGNORE_PEP}" \
		$(SOURCE_GLOB)

.PHONY: flake8
flake8:
	flake8 \
		--ignore="${IGNORE_PEP}" \
		$(SOURCE_GLOB)

.PHONY: mypy
mypy:
	MYPYPATH=stubs/ mypy \
		$(SOURCE_GLOB)

.PHONY: pytype
pytype:
	pytype scaffold/ --disable=import-error,pyi-error

.PHONY: install
install:
	pip3 install -r requirements.txt
	pip3 install -r requirements-dev.txt

.PHONY: pytest
pytest:
	pytest tests/

.PHONY: test-unit
test-unit: pytest

.PHONY: test
test: lint pytest

code:
	code .

.PHONY: dist
dist:
	python3 setup.py sdist bdist_wheel

.PHONY: publish
publish:
	PATH=~/.local/bin:${PATH} twine upload dist/*

.PHONY: version
version:
	@newVersion=$$(awk -F. '{print $$1"."$$2"."$$3+1}' < VERSION) \
		&& echo $${newVersion} > VERSION \
		&& echo VERSION = \'$${newVersion}\' > src/version.py \
		&& git add VERSION src/version.py \
		&& git commit -m "$${newVersion}" > /dev/null \
		&& git tag "$${newVersion}" \
		&& echo "Bumped version to $${newVersion}"

.PHONY: deploy-version
deploy-version:
	echo "VERSION = '$$(cat VERSION)'" > src/scaffold/version.py