# Makefile for org-mgmt project to streamline Poetry commands

# Run the Streamlit application
run-streamlit:
	poetry run streamlit run main.py

# Install project dependencies as per pyproject.toml
install-dependencies:
	poetry install

# Add a new package dependency (usage: make add-package pkg=<package-name>)
add-package:
	poetry add $(pkg)

# Update all project dependencies
update-dependencies:
	poetry update

# Show Poetry-managed virtual environment info
show-venv:
	poetry env info

# Activate Poetry shell environment (note: requires poetry shell plugin)
activate-shell:
	poetry shell

# Run pytest for testing
test:
	poetry run pytest

# Show list of installed packages
show-packages:
	poetry show

# Clean Poetry cache
clean-cache:
	poetry cache clear pypi --all

# Remove virtual environment
remove-venv:
	poetry env remove $$(poetry env list --full-path | head -n 1)

# Format code using isort and black
format:
	poetry run isort .
	poetry run black .

# Run linter using flake8
lint:
	poetry run flake8 .

# Run static type checker using mypy
typecheck:
	poetry run mypy .

autofix-unused:
	poetry run autoflake --in-place --remove-unused-variables --remove-all-unused-imports -r .

# Validate runs formatting, linting, and type checking sequentially
validate: autofix-unused format lint typecheck
