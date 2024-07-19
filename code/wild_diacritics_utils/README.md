# Wild Diacritics Utils

## Description

This is a repository of some python scripts that were used for the wild diacritics project which was created to analyse the random diacritical marks placed in normal arabic writing and attempting to use those in order to improve CAMeL tools automatic arabic diacritization models.

## Setup

install the required pip packages using the following command

```bash
pip install -r requirements.txt
```

Also you also need to change the relative path of the `diac_handler.py` and `token_handler.py` in the lines that import these files as follows:

```python
exec(open('<RELATIVE_PATH_TO_HANDLER>').read())
```

 in any of the scripts when using them so that these relative paths really point towards `diac_handler.py` and `token_handler.py`

## Overview

This repository has modules and scripts, modules are python files with a lot of helper functions for resusability between different scripts.

#### Modules
- [token\_handler.py](modules/token_handler)
- [diac\_handler.py](modules/diac_handler)

#### Scripts
- [tokenize\_normalize.py](scripts/tokenize_normalize)
- [diac\_stats.py](scripts/diac_stats)
- [compare\_diac.py](scripts/compare_diac)
- AND MORE


## Dependencies
- [camel-tools](https://pypi.org/project/camel-tools/)
- [Levenshtein](https://pypi.org/project/python-Levenshtein/)


## DEV NOTES

- to get a list of python versions
```bash
pyenv install --list
```
- to download one version
```bash
pyenv install 3.10.13
```
- to change the python version of the current shell use
```bash
pyenv shell 3.10.13
```
- to create a new virtual environment use
```bash
python -m venv wild_diac_env
```
- in order to activate the python environment use
```bash
source wild_diac_env/bin/activate
```
- and to deactivate use
```bash
deactivate
```
- In order to reinstall camel\_tools use
```bash
pip install -e .
pyenv rehash
```
