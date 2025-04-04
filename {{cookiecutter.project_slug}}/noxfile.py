import fileinput
import nox
from rtoml import load
import sys
from datetime import datetime, timezone
from pathlib import Path
from python_active_versions.python_active_versions import get_active_python_versions
from typing import List

from {{ cookiecutter.pkg_name }} import _project
from {{ cookiecutter.pkg_name }}.bundle import get_bundle_dir
from {{ cookiecutter.pkg_name }}.models import EnvVars
from {{ cookiecutter.pkg_name }}.pipeline import gather_data


def _get_active_version(_active_versions: List[dict]) -> List[str]:
    return [_av['version'] for _av in _active_versions]


_python_versions = _get_active_version(get_active_python_versions())


def dev_commands(session):
    session.run("poetry", "run", "python", "--version", external=True)
    session.run("python", "--version", external=True)
    session.run("poetry", "lock", external=True)
    session.run("poetry", "sync", "-v", "--with", "devel", "--no-root", external=True)
    session.run("poetry", "run", "nox", "--version", external=True)
    session.run("poetry", "run", "pip", "--version", external=True)
    session.run("poetry", "run", "pip", "list", "--format=freeze", external=True)


@nox.session(name="format")
def format_code(session):
    """Format the code"""
    dev_commands(session)
    session.run("poetry", "run", "isort", "{{ cookiecutter.pkg_name }}", "tests", "docs", "noxfile.py",
                external=True)
    session.run("poetry", "run", "black", "{{ cookiecutter.pkg_name }}", "tests", "docs", "noxfile.py",
                external=True)


@nox.session(name="license")
def update_license(session):
    """License files according to REUSE 3.0"""
    dev_commands(session)
    _year = str(datetime.now().year)

    # files correctly managed by reuse from their extension
    session.log('files recognized by extension')
    _py = list(Path().glob('./{{ cookiecutter.pkg_name }}/**/*.py'))
    _py = list(Path().glob('./*.py'))
    _py.extend(list(Path().glob('./tests/**/*.py')))
    _py.extend(list(Path().glob('./docs/**/*.py')))
    _py.extend(list(Path().glob('./.github/**/*.yml')))
    _py.extend(Path().glob('./.github/**/*.yaml'))
    _py.extend(list(Path().glob('./docs/Makefile')))
    _py.extend(list(Path().glob('./docs/make.bat')))
    _py.extend(list(Path().glob('./pyproject.toml')))
    if _py:
        session.run("poetry",
                    "run",
                    "reuse",
                    "annotate",
                    "--license={{ cookiecutter.open_source_license }}",
                    "--copyright={{ cookiecutter.full_name.replace('\"', '\\\"') }}",
                    f"--year={_year}",
                    "--merge-copyrights",
                    *_py,
                    external=True)

    # dot-file license
    session.log('dot-file license')
    _dot = list(Path().glob('./{{ cookiecutter.pkg_name }}/**/*.json'))
    _dot.extend(list(Path().glob('./tests/**/*.json')))
    _dot.extend(list(Path().glob('./docs/**/*.json')))
    _dot.extend(list(Path().glob('./**/*.rst')))
    _dot.extend(list(Path().glob('./**/*.md')))
    _dot.extend(list(Path().glob('./**/*.lock')))
    _dot.extend(list(Path().glob('./**/*.cfg')))
    _dot.extend(list(Path().glob('./**/py.typed')))
    _dot.extend(list(Path().glob('./**/*.sqlite')))
    _v_not_nox = [x for x in _dot if not x.parts[0].startswith(".nox")]
    _v_not_gen = [x for x in _v_not_nox if '_generated' not in x.parts]
    if _v_not_gen:
        session.run("poetry",
                    "run",
                    "reuse",
                    "annotate",
                    "--license={{ cookiecutter.open_source_license }}",
                    "--copyright={{ cookiecutter.full_name.replace('\"', '\\\"') }}",
                    f"--year={_year}",
                    "--merge-copyrights",
                    "--force-dot-license",
                    *_v_not_gen,
                    external=True)

    # dot-files - forced python style
    session.log('forced python style')
    _dot_files = list(Path().glob('./.editorconfig'))
    _dot_files.extend(list(Path().glob('./.gitignore')))
    _dot_files.extend(list(Path().glob('./.yamllint')))
    _dot_files.extend(list(Path().glob('./.pre-commit-config.yaml')))
    _dot_files.extend(list(Path().glob('./hadolint.yaml')))
    _dot_files.extend(list(Path().glob('./trivy.yaml')))
    _dot_files.extend(list(Path().glob('./Dockerfile')))
    if _dot_files:
        session.run("poetry",
                    "run",
                    "reuse",
                    "annotate",
                    "--license={{ cookiecutter.open_source_license }}",
                    "--copyright={{ cookiecutter.full_name.replace('\"', '\\\"') }}",
                    f"--year={_year}",
                    "--merge-copyrights",
                    "--style",
                    "python",
                    *_dot_files,
                    external=True)

    # download license
    session.run("poetry", "run", "reuse", "download", "--all", external=True)

    # fix license file
    _creation_year = "{% now 'utc', '%Y' %}"
    REGEX_REPLACEMENTS = [
        (r"<year>", f"{_creation_year}"),
        (r"<copyright holders>", "Gabriele Pongelli"),
        (r"20[0-9]{2} - 20[0-9]{2}", f"{_creation_year} - {_year}"),
    ]
    _license_file = get_bundle_dir() / 'LICENSES/{{ cookiecutter.open_source_license }}.txt'
    with _license_file as f:
        session.log('license files')
        _text = f.read_text()
        for old, new in REGEX_REPLACEMENTS:
            _text = sub(old, new, _text)

        if (_year not in _text) and (f"{_creation_year} - " not in _text):
            _text = sub(f"{_creation_year}", f"{_creation_year} - {_year}", _text)

        f.write_text(_text)


@nox.session
def lint(session):
    """Lint the code"""
    build(session)

    session.run("poetry", "install", external=True)
    session.run("poetry", "run", "flake8", "{{ cookiecutter.pkg_name }}", "tests", external=True, success_codes=[0, 1])
    {%- if cookiecutter.use_mypy == 'y' %}
    session.run("poetry", "run", "mypy", "--install-types", "{{ cookiecutter.pkg_name }}", "tests", external=True, success_codes=[0, 1])
    {%- endif %}
    session.run("poetry", "run", "yamllint", "-f", "colored", "{{ cookiecutter.pkg_name }}", external=True)
    session.run("poetry", "run", "codespell", "{{ cookiecutter.pkg_name }}", "docs/source", external=True)
    session.run("poetry", "run", "pylint", "{{ cookiecutter.pkg_name }}", external=True)
    session.run("poetry", "run", "darglint", "-v", "2", "{{ cookiecutter.pkg_name }}", external=True)
    session.run("poetry", "run", "bandit", "-r", "{{ cookiecutter.pkg_name }}", external=True)
    session.run("poetry", "run", "ruff", "check", "{{ cookiecutter.pkg_name }}", external=True)
    session.run("poetry", "run", "reuse", "lint", external=True)
    # session.run("poetry", "run", "python-active-versions", external=True)
    session.run("poetry", "run", "check-python-versions", ".", external=True, success_codes=[0, 1])  # avoid stage failure


def _build(session):
    session.run("poetry", "build", external=True)
    session.run("poetry", "run", "twine", "check", "dist/*", external=True)


@nox.session
def build(session):
    """Build package"""
    dev_commands(session)
    _build(session)


@nox.session
def docs(session):
    """Build docs"""
    dev_commands(session)

    {%- if 'mkdocs' in cookiecutter.doc_generator|lower %}
    session.run("poetry", "run", "mkdocs", "build",
                env={'PY_PKG_YEAR': str(datetime.now().year)}, external=True)
    {%- else %}
    session.run("poetry", "run", "sphinx-build", "-b", "html", "docs/source/", "docs/build/html",
                env={'PY_PKG_YEAR': str(datetime.now().year)}, external=True)
    {%- endif %}


@nox.session(python=_python_versions)
def test(session):
    _plat = sys.platform

    # print(f"py: {session.python}")

    if _plat == 'win32':
        _pyth = 'python'
    else:
        _pyth = f"python{session.python}"

    session.env['COVERAGE_FILE'] = f'.coverage_{session.name}'
    session.env['PYTHONWARNINGS'] = 'ignore'

    session.run("poetry", "env", "use", _pyth, external=True)

    build(session)
    session.run("poetry", "install", external=True)

    if session.posargs:
        # explicitly pass test file to nox -> nox -- test.py
        test_files = session.posargs
    else:
        # call nox without arguments
        test_files = list(Path().glob('./tests/**/*.py'))

    session.run(
        'poetry',
        'run',
        'pytest',
        *test_files,
        f"--cov-report=html:html_coverage_{session.name}",
        f"--cov-report=xml:xml_coverage_{session.name}.xml",
        external=True
    )


@nox.session
def release(session):
    """Run release task"""
    dev_commands(session)

    session.run("poetry", "run", "cz", "-nr", "3", "bump", "--changelog", "--yes", external=True)
    _build(session)
    # session.run("poetry", "run", "PyInstaller", "jazz_reports.spec", external=True)
    # session.run("poetry", "publish", "-r", "...", external=True)


@nox.session(name='container')
def container_build(session):
    git_hash = session.run(
        "poetry", "run", "git", "rev-parse", "HEAD",
        external=True, silent=True
    )

    os.environ['GIT_COMMIT'] = git_hash.strip()
    _v = EnvVars(**os.environ)
    _project.env_vars = _v

    _pyproject_data = gather_data("useless-in-local-build")

    _podman_args = [f'--build-arg={k}={v}' for k, v in _pyproject_data.items()]

    session.run(
        "podman",
        "build",
        "-t",
        f"{_project.IMAGE_NAME}:{_project.IMAGE_VERSION}",
        *_podman_args,
        # <build-args-here>
        "--no-cache",
        "--format",
        "docker",
        ".",
        external=True,
    )


@nox.session()
def container_lint(session):
    hadolint(session)

    trivy(session)

    # this works on downloaded images from dockerhub; only way to work on local built images is through tar file
    # "podman run -v /var/run/docker.sock:/var/run/docker.sock -v ./trivy_cache:/root/.cache/
    #   -v ./trivy.yaml:/root/trivy.yaml aquasec/trivy:0.53.0 -c /root/trivy.yaml
    #   image gpongelli/python-active-versions:1.17.2"

    dive(session)



@nox.session()
def dive(session):
    session.run(
        "podman",
        "run",
        "--rm",
        "-e",
        "CI=true",
        "-v",
        "/var/run/docker.sock:/var/run/docker.sock",
        "wagoodman/dive:latest",
        f"{_pyproject_data['IMAGE_NAME']}:{_pyproject_data['IMAGE_VERSION']}",
        external=True,
        success_codes=[0, 1],
    )


@nox.session()
def hadolint(session):
    session.run(
        "podman",
        "run",
        "--rm",
        # "-it",
        "-v",
        "Dockerfile:/Dockerfile",
        "-v",
        "hadolint.yaml:/hadolint.yaml",
        "ghcr.io/hadolint/hadolint",
        "hadolint",
        "--config",
        "/hadolint.yaml",
        "/Dockerfile",
        external=True,
        success_codes=[0, 1],
    )


@nox.session(requires=["container"])
def trivy(session):
    _trivy_image = "aquasec/trivy:0.60.0"

    # create trivy cache folder if not exist
    os.makedirs('trivy_cache', exist_ok=True)

    # run trivy on local project
    session.run(
        "podman",
        "run",
        "-v",
        "/var/run/docker.sock:/var/run/docker.sock",
        "-v",
        ".:/root/proj",
        "-v",
        "./trivy_cache:/root/.cache/",
        "-v",
        "./trivy.yaml:/root/trivy.yaml",
        _trivy_image,
        "-c",
        "/root/trivy.yaml",
        "fs",
        "/root/proj",
        external=True,
        success_codes=[0, 1],
    )

    # run trivy scan
    session.run(
        "podman",
        "run",
        "--rm",
        "-v",
        "/var/run/docker.sock:/var/run/docker.sock",
        "-v",
        ".:/root/proj",
        "-v",
        "./trivy_cache:/root/.cache/",
        "-v",
        "./trivy.yaml:/root/trivy.yaml",
        _trivy_image,
        "-c",
        "/root/trivy.yaml",
        "image",
        f"localhost/{_project.IMAGE_NAME}:{_project.IMAGE_VERSION}",
        external=True,
        success_codes=[0, 1],
    )


# https://www.jit.io/resources/appsec-tools/a-guide-to-generating-sbom-with-syft-and-grype

@nox.session(requires=["container"])
def syft(session):
    _tool_image = "anchore/syft:v1.20.0"

    # https://github.com/anchore/syft , could be useful a local config file ?

    # run tool on local project
    session.run(
        "podman",
        "run",
        "--rm",
        "-v",
        "/var/run/docker.sock:/var/run/docker.sock",
        "-v",
        ".:/tmp/proj",
        _tool_image,
        "scan",
        "--scope",
        "all-layers",
        "--enrich",
        "all",
        "-o",
        "syft-json=/tmp/proj/sbom.syft.json",  # out file
        "-o",
        "spdx-json=/tmp/proj/sbom.spdx.json",  # out file
        f"localhost/{_project.IMAGE_NAME}:{_project.IMAGE_VERSION}",
        external=True,
        success_codes=[0, 1],
    )


@nox.session(requires=["container"])
def grype(session):
    _tool_image = "anchore/grype:v0.89.0"

    # https://github.com/anchore/grype , could be useful a local config file ?

    # run tool on local project
    session.run(
        "podman",
        "run",
        "--rm",
        "-v",
        "/var/run/docker.sock:/var/run/docker.sock",
        "-v",
        ".:/tmp/proj",
        _tool_image,
        "-o",
        "json",  # out file
        "--file",
        "/tmp/proj/grype.json",  # out file
        f"localhost/{_project.IMAGE_NAME}:{_project.IMAGE_VERSION}",
        external=True,
        success_codes=[0, 1],
    )
