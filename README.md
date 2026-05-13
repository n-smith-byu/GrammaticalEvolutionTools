# Grammatical Evolution Tools

[![Python Version](https://img.shields.io/badge/python-3.13+-blue)](https://www.python.org/downloads/)
[![PyPI](https://img.shields.io/pypi/v/GrammaticalEvolutionTools)](https://pypi.org/project/GrammaticalEvolutionTools/)
[![GitHub License](https://img.shields.io/badge/License-MIT-green)](https://github.com/n-smith-byu/GrammaticalEvolutionTools/blob/main/LICENSE)
![Docs](https://img.shields.io/badge/docs-coming--soon-yellow)
![Tests](https://img.shields.io/badge/tests-in--development-yellow)


## Table of Contents
* [Introduction](#introduction)
* [Features](#features)
    * [Currently Available](#currently-available)
    * [Coming Soon](#coming-soon) 
* [Installation](#installation)
    * [PyPI](#pypi)
    * [Local Development](#local-development)
        * [Prerequisites](#prerequisites)
        * [Core Package](#core-package)
        * [For Notebooks and Examples](#for-notebooks-and-examples)
        * [For Development](#for-development-tests-and-docs)
* [Examples](#examples)
* [Running Tests](#running-tests)
* [Documentation](#documentation)
* [License](#license)

---

## Introduction

`GrammaticalEvolutionTools` is a Python package designed to simplify the setup and execution of Grammatical Evolution (GE) and other Agent-Based Modeling (ABM) projects. It provides a suite of tools for quickly spinning up worlds, defining grammars, setting up agents, and running and animating simulations. It includes a number of abstract classes you can easily inherit from and customize, with much of the underlying functionality already implemented.

Whether you're building complex simulation environments or simple test cases, `getools` streamlines the boilerplate, enabling faster iteration and more effective research in grammatical evolution.

*Note: This project is still in development. Code has been refactored and not all docstrings may reflect this yet.*

## Features

### Currently Available:
* **World Environment Setup:** Easily define and configure custom environments for GE agents.
* **Grammar Definition:** Inherit from common classes to create custom grammars with specific functionalities. 
* **Agent Management:** Logic for running Agent programs and having them interact with their world. 
* **Evolution:** Common methods for cross over and mutation, built to work with program trees.
* **Animation:** Create customizable animations for simulations.

### Coming Soon: 
* Asynchronous Behavior Trees!

## Installation

### PyPI

This package is available on PyPI. You can install it with:
```bash
pip install GrammaticalEvolutionTools
```

For pre-releases, you may need to specify the version:
```bash
pip install GrammaticalEvolutionTools==<VERSION>
```

After installation:

```python
import getools

from getools.worlds.grid_world import GridWorld
from getools.grammars import Grammar
...
world = GridWorld(...)
```

### Local Development

#### Prerequisites

This project uses [Poetry](https://python-poetry.org/) for dependency management and packaging. Before installing the package, ensure you have Poetry installed on your system.

The recommended way to install Poetry is using `pipx`, which installs Python applications in isolated environments.

```bash
# 1. Install pipx (if you don't have it)
python -m pip install --user pipx
python -m pipx ensurepath

# 2. Install Poetry using pipx
pipx install poetry
```

You can find more detailed installation instructions for Poetry on their official website: [Poetry Installation Guide](https://python-poetry.org/docs/#installation)

---

#### Core Package

To install the core package with only its essential dependencies (for integrating it into your own projects):

```bash
# Clone the repository
git clone https://github.com/n-smith-byu/GrammaticalEvolutionTools.git
cd GrammaticalEvolutionTools

# Install the core package
poetry install
```

#### For Notebooks and Examples

If you plan to explore the provided examples or run the Jupyter notebooks, you'll need to install the package with the `examples` dependency group.

```bash
# Install the package with examples dependencies
poetry install --with examples
```

#### For Development (Tests and Docs)

If you intend to modify the code, run tests, or build the documentation, install with the `dev` dependency group.

```bash
# Install in editable mode with dev dependencies
poetry install --with dev
```

---

## Examples

The `examples/` directory in this repository contains various Jupyter notebooks and scripts demonstrating how to use `getools` for different scenarios.

To run these examples, make sure you have installed the package with the `examples` dependency group:

```bash
# Ensure you are in the project root directory
cd examples/
jupyter lab # or jupyter notebook
```
Examples include an implementation of the Santa Fe problem and a basic grammatical evolution algorithm. 

---

## Running Tests 

*NOTE: Incomplete*

If you are developing the package, you can run the test suite using `pytest`. Ensure you have installed the `dev` dependencies.

```bash
# From the project root directory
pytest
```

---

## Documentation

*NOTE: Incomplete*

The project's documentation is built using Sphinx. To generate the HTML documentation locally, ensure you have installed the `dev` dependencies.

First, navigate to the `docs/` directory from the project root:

```bash
cd docs/
```

Then, run the appropriate command for your operating system:

**For Linux / macOS / WSL:**
```bash
make html
```

**For Windows (Command Prompt / PowerShell):**
```bash
poetry run sphinx-build -b html . _build/html
```

The generated HTML documentation will be located in `docs/_build/html/index.html`. You can open this file in your web browser to view the documentation.

---

## License

This project is licensed under the [MIT License](https://github.com/n-smith-byu/GrammaticalEvolutionTools/blob/main/LICENSE).


---

