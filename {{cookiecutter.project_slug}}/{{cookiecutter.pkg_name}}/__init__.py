"""Top-level package for {{ cookiecutter.project_name }}."""

import logging
import tomllib
from {{cookiecutter.pkg_name}}.models import PyprojectModel


try:
    from icecream import ic, install

    # installing icecream
    install()
    ic.configureOutput(outputFunction=logging.debug, includeContext=True)
except ImportError:  # Graceful fallback if IceCream isn't installed.
    ic = lambda *a: None if not a else (a[0] if len(a) == 1 else a)  # noqa


_project = PyprojectModel()

__author__ = _project.pyproject_settings.authors[0].name
__email__ = _project.pyproject_settings.authors[0].email
__version__ = _project.pyproject_settings.version

__description__ = _project.pyproject_settings.description
__project_name__ = _project.pyproject_settings.name
