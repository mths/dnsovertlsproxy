# @author matheus bessa

MODULE=dnsovertlsproxy
.PHONY:

run:
	python -m ${MODULE}

python-build:
	@echo "Running build/install using setup.py"
	@python setup.py install

python-clean:
	@echo "Cleaning python cache files and directories..."
	@find . -name '*.pyc' | xargs -r rm
	@find . -name '__pycache__' | xargs -r rm -rf
	@find . -name '*.egg-info' | xargs -r rm -rf
	@rm -rf build
	@rm -rf dist

python-lint:
	@echo "Running linter for python..."
	@flake8 ${MODULE}

dockerfile-lint:
	@echo "Running linter for Dockerfile..."
	@docker run --rm -i hadolint/hadolint < Dockerfile

