import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from tomllib import load
from typing import Dict

sys.path.insert(0, '.')

from {{cookiecutter.pkg_name}} import _project
from {{cookiecutter.pkg_name}}.models  import SubModels


def get_bundle_dir() -> Path:
    """Return bundle dir, different in case of binary file.

    Returns:
        folder as Path object.
    """
    if getattr(sys, 'frozen', False):
        # we are running in a bundle
        bundle_dir = Path(sys._MEIPASS)  # type: ignore  # pylint: disable=W0212
    else:
        # we are running in a normal Python environment
        bundle_dir = Path.cwd()
        if 'PY_PKG_YEAR' in os.environ:
            # nox pass PY_PKG_YEAR env var, and its cwd is into docs/source
            bundle_dir = bundle_dir / '..' / '..'

    return bundle_dir


def gather_data(ci_env_var_filename: str) -> Dict[str, str]:
    _project_vars = _project.model_dump(exclude={SubModels.dl_settings, SubModels.poetry_settings,
                                                 SubModels.pyproject_settings, SubModels.env_vars, SubModels.env_file})

    if _project.env_vars.ci and not _project.env_vars.git_commit:
        raise KeyError('GIT_COMMIT not present in pipeline, be sure to remove "skipDefaultCheckout true"')

    _ci_export = [f"export {k}='{v}'\n" for k, v in _project_vars.items()]

    if _project.env_vars.ci:
        with open(Path.cwd() / ci_env_var_filename, mode='w') as out_env:
            out_env.write('#!/bin/bash\n\n')
            out_env.writelines(_ci_export)

    return _project_vars


if __name__ == "__main__":
    _filename = "pipeline_env_vars.sh"
    if len(sys.argv) > 1:
        _filename = sys.argv[1]

    # create file for pipeline and just dump it
    print(gather_data(_filename))
