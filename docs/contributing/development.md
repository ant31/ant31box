# Contributing: Development Setup

We welcome contributions! This guide will help you set up your development environment to work on `ant31box`.

## 1. Prerequisites

-   Python 3.12 or later.
-   [uv](https://github.com/astral-sh/uv): A fast Python package installer and resolver.

## 2. Fork and Clone the Repository

First, fork the `ant31box` repository on GitHub, and then clone your fork to your local machine.

```bash
git clone https://github.com/YOUR_USERNAME/ant31box.git
cd ant31box
```

## 3. Set Up the Virtual Environment

We use `uv` to manage our virtual environments and dependencies.

```bash
# Create a virtual environment
uv venv

# Activate the virtual environment
source .venv/bin/activate
```

## 4. Install Dependencies

Install the project in editable mode with all development and optional dependencies.

```bash
# Install all dependencies from uv.lock
uv sync -d
```
The `sync -d` command installs all dependencies from the `[project]` and `dev` groups defined in `pyproject.toml`, using the versions pinned in `uv.lock`.

## 5. Running Linters and Formatters

We use `ruff` for linting, formatting, and import sorting. The configuration is in `pyproject.toml` and `ruff.toml`. We also use `pyright` for static type checking.

You can run these checks using the `Makefile`:

```bash
# Check formatting, import order, and linting
make check

# Automatically fix formatting and linting issues
make fix

# Run the pyright type checker
make pyright
```
It is highly recommended to set up a pre-commit hook to run these checks automatically before you commit your changes.

## 6. Running Tests

The test suite is run using `pytest`. The `Makefile` provides a convenient command to run all tests with coverage reporting.

```bash
make test
```
This command will run all tests in the `tests/` directory and generate a coverage report in the console and as an HTML report in the `htmlcov/` directory.

## 7. Building the Documentation

The documentation is built with `mkdocs`.

```bash
# Serve the documentation locally with live-reloading
make serve-docs

# Build the static documentation site (output in the `site/` directory)
make docs
```

You are now ready to start contributing to `ant31box`!
