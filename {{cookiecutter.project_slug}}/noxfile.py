import nox
import sys
from datetime import datetime
from pathlib import Path
from python_active_versions.python_active_versions import get_active_python_versions
from typing import List


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
    session.run("poetry", "run", "isort", "{{ cookiecutter.pkg_name }}", "tests",
                external=True)
    session.run("poetry", "run", "black", "{{ cookiecutter.pkg_name }}", "tests",
                external=True)


@nox.session
def update_license(session):
    """License files according to REUSE 3.0"""
    dev_commands(session)
    _year = str(datetime.now().year)

    # python files
    _py = list(Path().glob('./{{ cookiecutter.pkg_name }}/*.py'))
    _py = list(Path().glob('./*.py'))
    _py.extend(list(Path().glob('./tests/*.py')))
    _py.extend(list(Path().glob('./docs/*.py')))
    _absolute = list(map(lambda x: x.absolute(), _py))
    if _absolute:
        session.run("poetry", "run", "reuse", "annotate", "--license={{ cookiecutter.open_source_license }}", "--copyright={{ cookiecutter.full_name.replace('\"', '\\\"') }}",
                    f"--year={_year}", "--merge-copyrights", *_absolute,
                    external=True)

    # json dotted license
    _dot = list(Path().glob('./{{ cookiecutter.pkg_name }}/*.json'))
    _dot.extend(list(Path().glob('./tests/*.json')))
    _dot.extend(list(Path().glob('./docs/*.json')))
    if _dot:
        session.run("poetry", "run", "reuse", "annotate", "--license={{ cookiecutter.open_source_license }}", "--copyright={{ cookiecutter.full_name.replace('\"', '\\\"') }}",
                    f"--year={_year}", "--merge-copyrights", "--force-dot-license", *_dot,
                    external=True)

    # yaml - md
    _yaml = list(Path().glob('./github/*.yml'))
    _yaml.extend(list(Path().glob('./github/*.md')))
    _yaml.extend(list(Path().glob('./docs/Makefile')))
    _yaml.extend(list(Path().glob('./docs/make.bat')))
    _yaml.extend(list(Path().glob('./pyproject.toml')))
    if _yaml:
        session.run("poetry", "run", "reuse", "annotate", "--license={{ cookiecutter.open_source_license }}", "--copyright={{ cookiecutter.full_name.replace('\"', '\\\"') }}",
                    f"--year={_year}", "--merge-copyrights", *_yaml,
                    external=True)

    # dot-files
    _dot_files = list(Path().glob('./.editorconfig'))
    _dot_files.extend(list(Path().glob('./.gitignore')))
    _dot_files.extend(list(Path().glob('./.yamllint')))
    _dot_files.extend(list(Path().glob('./.pre-commit-config.yaml')))
    if _dot_files:
        session.run("poetry", "run", "reuse", "annotate", "--license={{ cookiecutter.open_source_license }}", "--copyright={{ cookiecutter.full_name.replace('\"', '\\\"') }}",
                    f"--year={_year}", "--merge-copyrights", "--style", "python", *_dot_files,
                    external=True)

    # various files
    _various = list(Path().glob('./*.rst'))
    _various.extend(list(Path().glob('./*.md')))
    _various.extend(list(Path().glob('./*.lock')))
    _various.extend(list(Path().glob('./*.cfg')))
    if _various:
        session.run("poetry", "run", "reuse", "annotate", "--license={{ cookiecutter.open_source_license }}", "--copyright={{ cookiecutter.full_name.replace('\"', '\\\"') }}",
                    f"--year={_year}", "--merge-copyrights", "--force-dot-license", *_various,
                    external=True)

    # download license
    session.run("poetry", "run", "reuse", "download", "--all")

    # fix license file
    with Path(Path.cwd() / 'LICENSES/{{ cookiecutter.open_source_license }}.txt') as f:
        _text = f.read_text()
        _text.replace('{% now 'utc', '%Y' %} {{ cookiecutter.full_name.replace('\"', '\\\"') }}', f'{% now 'utc', '%Y' %} - {_year} {{ cookiecutter.full_name.replace('\"', '\\\"') }}').replace('<year>', '{% now 'utc', '%Y' %}').replace('<copyright holders>', '{{ cookiecutter.full_name.replace('\"', '\\\"') }}')
        f.write_text(_text)


@nox.session
def lint(session):
    """Lint the code"""
    dev_commands(session)

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
    session.run("poetry", "run", "reuse", "lint", external=True)
    # session.run("poetry", "run", "python-active-versions", external=True)
    session.run("poetry", "run", "check-python-versions", ".", external=True)


@nox.session
def build(session):
    """Build package"""
    dev_commands(session)
    session.run("poetry", "build", external=True)
    session.run("poetry", "run", "twine", "check", "dist/*", external=True)


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
    session.run("poetry", "build", external=True)
    session.run("poetry", "run", "twine", "check", "dist/*", external=True)
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
