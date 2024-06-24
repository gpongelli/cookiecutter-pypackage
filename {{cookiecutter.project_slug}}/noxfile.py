import fileinput
import nox
from rtoml import load
import sys
from datetime import datetime
from pathlib import Path
from python_active_versions.python_active_versions import get_active_python_versions
from typing import List

from {{ cookiecutter.pkg_name }} import __version__
from {{ cookiecutter.pkg_name }}.bundle import get_bundle_dir


def _get_active_version(_active_versions: List[dict]) -> List[str]:
    return [_av['version'] for _av in _active_versions]


_python_versions = _get_active_version(get_active_python_versions())


def dev_commands(session):
    session.run("poetry", "run", "python", "--version", external=True)
    session.run("python", "--version", external=True)
    session.run("poetry", "lock", "--no-update", external=True)
    session.run("poetry", "install", "-v", "--with", "devel", "--no-root", "--sync", external=True)
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


@nox.session
def update_license(session):
    """License files according to REUSE 3.0"""
    dev_commands(session)
    _year = str(datetime.now().year)

    # files correctly managed by reuse from their extension
    session.log('files recognized by extension')
    _py = list(Path().glob('./{{ cookiecutter.pkg_name }}/*.py'))
    _py = list(Path().glob('./*.py'))
    _py.extend(list(Path().glob('./tests/*.py')))
    _py.extend(list(Path().glob('./docs/*.py')))
    _py.extend(list(Path().glob('./.github/**/*.yml')))
    _py.extend(Path().glob('./.github/**/*.yaml'))
    _py.extend(list(Path().glob('./docs/Makefile')))
    _py.extend(list(Path().glob('./docs/make.bat')))
    _py.extend(list(Path().glob('./pyproject.toml')))
    if _py:
        session.run("poetry", "run", "reuse", "annotate", "--license={{ cookiecutter.open_source_license }}", "--copyright={{ cookiecutter.full_name.replace('\"', '\\\"') }}",
                    f"--year={_year}", "--merge-copyrights", *_py,
                    external=True)

    # dot-file license
    session.log('dot-file license')
    _dot = list(Path().glob('./{{ cookiecutter.pkg_name }}/*.json'))
    _dot.extend(list(Path().glob('./tests/*.json')))
    _dot.extend(list(Path().glob('./docs/*.json')))
    _dot.extend(list(Path().glob('./**/*.rst')))
    _dot.extend(list(Path().glob('./**/*.md')))
    _dot.extend(list(Path().glob('./**/*.lock')))
    _dot.extend(list(Path().glob('./**/*.cfg')))
    _dot.extend(list(Path().glob('./**/py.typed')))
    _v_not_nox = [x for x in _dot if not x.parts[0].startswith(".nox")]
    _v_not_gen = [x for x in _v_not_nox if '_generated' not in x.parts]
    if _v_not_gen:
        session.run("poetry", "run", "reuse", "annotate", "--license={{ cookiecutter.open_source_license }}", "--copyright={{ cookiecutter.full_name.replace('\"', '\\\"') }}",
                    f"--year={_year}", "--merge-copyrights", "--force-dot-license", *_v_not_gen,
                    external=True)

    # dot-files - forced python style
    session.log('forced python style')
    _dot_files = list(Path().glob('./.editorconfig'))
    _dot_files.extend(list(Path().glob('./.gitignore')))
    _dot_files.extend(list(Path().glob('./.yamllint')))
    _dot_files.extend(list(Path().glob('./.pre-commit-config.yaml')))
    _dot_files.extend(list(Path().glob('./Dockerfile')))
    if _dot_files:
        session.run("poetry", "run", "reuse", "annotate", "--license={{ cookiecutter.open_source_license }}", "--copyright={{ cookiecutter.full_name.replace('\"', '\\\"') }}",
                    f"--year={_year}", "--merge-copyrights", "--style", "python", *_dot_files,
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
    _license_file = Path.cwd() / 'LICENSES/{{ cookiecutter.open_source_license }}.txt'
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
    dev_commands(session)

    session.run("poetry", "build", external=True)
    session.run("poetry", "install", external=True)
    session.run("poetry", "run", "flake8", "{{ cookiecutter.pkg_name }}", "tests", external=True)
    {%- if cookiecutter.use_mypy == 'y' %}
    session.run("poetry", "run", "mypy", "--install-types", "{{ cookiecutter.pkg_name }}", "tests", external=True)
    {%- endif %}
    session.run("poetry", "run", "yamllint", "-f", "colored", "{{ cookiecutter.pkg_name }}", external=True)
    session.run("poetry", "run", "codespell", "{{ cookiecutter.pkg_name }}", "docs/source", external=True)
    session.run("poetry", "run", "pylint", "{{ cookiecutter.pkg_name }}", external=True)
    session.run("poetry", "run", "darglint", "-v", "2", "{{ cookiecutter.pkg_name }}", external=True)
    session.run("poetry", "run", "bandit", "-r", "{{ cookiecutter.pkg_name }}", external=True)
    session.run("poetry", "run", "ruff", "{{ cookiecutter.pkg_name }}", external=True)
    session.run("poetry", "run", "reuse", "lint", external=True)
    # session.run("poetry", "run", "python-active-versions", external=True)
    session.run("poetry", "run", "check-python-versions", ".", external=True, success_codes=[0, 1])  # avoid stage failure


def _build(session):
    with open(get_bundle_dir() / 'pyproject.toml', "r") as pyproj:
        pyproject = load(pyproj)
    __description = pyproject['tool']['poetry']['description']
    __project_name = pyproject['tool']['poetry']['name']

    with fileinput.FileInput(get_bundle_dir() / 'python_active_versions/__init__.py', inplace=True) as f:
        for line in f:
            if line.startswith('__description__'):
                print(f'__description__ = "{__description}"')
            elif line.startswith("__project_name__"):
                print(f'__project_name__ = "{__project_name}"')
            else:
                print(line, end='')
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

    dev_commands(session)
    _build(session)
    session.run("poetry", "install", external=True)

    if session.posargs:
        # explicitly pass test file to nox -> nox -- test.py
        test_files = session.posargs
    else:
        # call nox without arguments
        test_files = list(Path().glob('./tests/*.py'))

    session.run('poetry', 'run', 'pytest', *test_files, f"--cov-report=html:html_coverage_{session.name}",
                f"--cov-report=xml:xml_coverage_{session.name}.xml", external=True)


@nox.session
def release(session):
    """Run release task"""
    dev_commands(session)

    session.run("poetry", "run", "cz", "-nr", "3", "bump", "--changelog", "--yes", external=True)
    session.run("poetry", "build", external=True)
    # session.run("poetry", "run", "PyInstaller", "jazz_reports.spec", external=True)
    # session.run("poetry", "publish", "-r", "...", external=True)


@nox.session(name='container')
def container_build(session):
    _build(session)
    session.run(
        "podman",
        "build",
        "-t",
        f"{{ cookiecutter.project_slug }}:{__version__}",
        f"--build-arg=PKG_VERSION={__version__}",
        ".",
        external=True,
    )
