"""Top-level package for {{ cookiecutter.project_name }}."""

import logging
import tomllib
from {{cookiecutter.pkg_name}}.bundle import get_bundle_dir


try:
    from icecream import ic, install

    # installing icecream
    install()
    ic.configureOutput(outputFunction=logging.debug, includeContext=True)
except ImportError:  # Graceful fallback if IceCream isn't installed.
    ic = lambda *a: None if not a else (a[0] if len(a) == 1 else a)  # noqa

__author__ = "{{ cookiecutter.full_name }}"
__email__ = "{{ cookiecutter.email }}"
__version__ = "{{ cookiecutter.version }}"

__description__ = None
__project_name__ = None
if not __description__ or not __project_name__:
    with open(get_bundle_dir() / 'pyproject.toml', "rb") as pyproj:
        pyproject = tomllib.load(pyproj)
    __description__ = pyproject['tool']['poetry']['description']
    __project_name__ = pyproject['tool']['poetry']['name']
