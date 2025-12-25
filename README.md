# Grammatical Evolution Tools

[![Python Version](https://img.shields.io/badge/python-3.14+-blue)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/Version-0.1.0-blue)](https://github.com/n-smith-byu/grammaticalevolutiontools)
[![GitHub License](https://img.shields.io/badge/License-MIT-green)](https://github.com/n-smith-byu/GrammaticalEvolutionTools/blob/main/LICENSE)

---

## Table of Contents
* [Introduction](#introduction)
* [Features](#features)
* [Installation](#installation)
    * [Prerequisites](#prerequisites)
    * [Core Package](#core-package)
    * [For Notebooks and Examples](#for-notebooks-and-examples)
    * [For Development](#for-development)
* [Quick Start / Usage](#quick-start--usage)
* [Examples](#examples)
* [Running Tests](#running-tests)
* [Documentation](#documentation)
* [License](#license)
* [Contact](#contact)

---

## Introduction

`grammaticalevolutiontools` is a Python package designed to simplify the setup and execution of Grammatical Evolution (GE) projects. It provides a suite of tools for quickly spinning up worlds, defining grammars, setting up agents, and running and animating simulations. It includes a number of abstract classes you can easily inherit from and customize, with much of the underlying functionality already implemented.

Whether you're building complex simulation environments or simple test cases, `grammaticalevolutiontools` streamlines the boilerplate, enabling faster iteration and more effective research in grammatical evolution.

*NOTE: I am working on documentation and testing*

## Features

* **World Environment Setup:** Easily define and configure custom environments for GE agents.
* **Grammar Definition:** Inherit from common classes to create custom grammars with specific functionalities. 
* **Agent Management:** 
* **Problem Domain Abstraction:** Abstract away common GE problem complexities.
* **Animation:** Create customizable animations for simulations. 

## Installation

Since this package is not yet published to PyPI, you will need to clone the repository and install it locally.

### Prerequisites

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


### Core Package

To install the core package with only its essential dependencies (for integrating it into your own projects):

```bash
# Clone the repository first
git clone [https://github.com/n-smith-byu/grammaticalevolutiontools.git](https://github.com/n-smith-byu/grammaticalevolutiontools.git)
cd grammaticalevolutiontools

# Install the core package in editable mode
poetry install --no-root --only main
```

### For Notebooks and Examples

If you plan to explore the provided examples or run the Jupyter notebooks, you'll need to install the package with the `examples` dependency group.

```bash
# If you haven't already, clone the repository and navigate into it
# git clone [https://github.com/n-smith-byu/grammaticalevolutiontools.git](https://github.com/n-smith-byu/grammaticalevolutiontools.git)
# cd grammaticalevolutiontools

# Install the package with examples dependencies
poetry install --with examples
```

### For Development

If you intend to modify the code, run tests, or build the documentation, install with the `dev` dependency group.

```bash
# If you haven't already, clone the repository and navigate into it
# git clone [https://github.com/n-smith-byu/grammaticalevolutiontools.git](https://github.com/n-smith-byu/grammaticalevolutiontools.git)
# cd grammaticalevolutiontools

# Install in editable mode with dev dependencies
poetry install --with dev
```

---

## Examples

The `examples/` directory in this repository contains various Jupyter notebooks and scripts demonstrating how to use `grammaticalevolutiontools` for different scenarios.

To run these examples, make sure you have installed the package with the `examples` group:

```bash
# Ensure you are in the project root directory
cd examples/
jupyter lab # or jupyter notebook
```
Examples include an implementation of the Santa Fe problem and a basic grammatical evolution algorthm. 

---

## Running Tests 

*NOTE: In Progress*

If you are developing the package, you can run the test suite using `pytest`. Ensure you have installed the `dev` dependencies.

```bash
# From the project root directory
pytest
```

---

## Documentation

*NOTE: In Progress*

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