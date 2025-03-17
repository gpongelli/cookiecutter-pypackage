import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from tomllib import load
from typing import Dict


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
    with open(get_bundle_dir() / 'pyproject.toml', mode="rb") as pyproj:
        pyproject = load(pyproj)

    _project_vars = {
        "IMAGE_TIMESTAMP": datetime.now(timezone.utc).isoformat(),
        "IMAGE_NAME": pyproject['tool']['poetry']['name'],
        "IMAGE_VERSION": pyproject['tool']['poetry']['version'],
        "IMAGE_SRC": pyproject['tool']['poetry']['repository'],
        "IMAGE_DOC": pyproject['tool']['poetry']['documentation'],
        "IMAGE_DESCRIPTION": pyproject['tool']['poetry']['description'],
        "IMAGE_AUTHORS": ', '.join(pyproject['tool']['poetry']['authors']),
        "IMAGE_LICENSE": pyproject['tool']['poetry']['license'],
        "IMAGE_URL": pyproject['tool']['poetry']['urls']['Docker'],
        "JFROG_URL": pyproject['datalogic-vars']['jfrog-url'],
        "JFROG_USER": pyproject['datalogic-vars']['jfrog-user'],
    }

    if 'CI' in os.environ:
        try:
            _project_vars["IMAGE_GIT_HASH"] = os.environ['GIT_COMMIT']
        except KeyError as ke:
            raise KeyError('GIT_COMMIT not present in pipeline, be sure to remove "skipDefaultCheckout true"') from ke

        _ci_export = [f"export {k}='{v}'\n" for k, v in _project_vars.items()]

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
