# List out available commands
default:
	@just --list

# Execute installation
setup:
	@echo "Setting up project."
	pip3 install --upgrade setuptools
	@echo "Installing testing dependencies."
	pip3 install -r requirements-test.txt
	@echo "Setting up project requirements."
	pip3 install -r requirements.txt
	@echo "Project setup complete!"

# Launch API in debug mode
run-debug:
	@echo "Running main app..."
	@python3 app.py --port 8080 --debug

# Launch API in production mode
run-prod:
	@echo "Running main app..."
	@python3 app.py --port 8080

# Build Docker image
build-docker:
	@echo "Building docker image..."
	docker build -t fizzbuzz-api:latest -f ./Dockerfile .
	@echo "Docker image built successfully!"

# Run pep8, black, mypy linters
lint:
	python -m pylint api/
	python -m flake8 api/
	python -m black -l 80 --check api/
	python -m mypy --ignore-missing-imports api/

# Clean unused files
clean:
	-@find ./ -name '*.pyc' -exec rm -f {} \;
	-@find ./ -name '__pycache__' -exec rm -rf {} \;
	-@find ./ -name 'Thumbs.db' -exec rm -f {} \;
	-@find ./ -name '*~' -exec rm -f {} \;
	-@rm -rf .pytest_cache
	-@rm -rf .cache
	-@rm -rf .mypy_cache
	-@rm -rf build
	-@rm -rf dist
	-@rm -rf *.egg-info
	-@rm -rf htmlcov
	-@rm -rf .tox/
	-@rm -rf docs/_build
	-@rm -rf .venv
	@echo "Cleaned out unused files and directories!"

# Run PyTest unit tests
pytest:
	@echo "Running unittest suite..."
	pytest -vv -rA
	-@find ./ -name '__pycache__' -exec rm -rf {} \;
	-@rm -rf .pytest_cache
	@echo "Cleaned up test environment"

coverage:
    coverage run --source=api --omit="*/__*.py,*/test_*.py" -m pytest
    coverage report

# Run Behave feature tests
behave:
	@echo "Running feature test suite..."
	behave ./tests/features/feature_tests/api_features

smoke-tests:
	@echo "Running smoke test suite..."
	python3 smoketests.py
