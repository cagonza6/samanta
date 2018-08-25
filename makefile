
help:
	clear;
	@echo "=========== Usage ===========";
	@echo "clean-pyc     : Removes all pyc files";
	@echo "test          : Run unit tests and doctests";
	@echo "document      : Runs sphinx to generate the documentation";
	@echo "install       : Install the package using pip";
	@echo "install-devel : Install the package using python in development mode";

clean-pyc:
	find . -name "*.pyc" -exec rm -rf {} \;

test:
	python3 src/runtest.py


document:
	cd docs; make html

install:
	pip install .

install-devel:
	python setup.py develop
