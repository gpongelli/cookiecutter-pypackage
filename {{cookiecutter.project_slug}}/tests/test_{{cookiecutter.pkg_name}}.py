#!/usr/bin/env python
"""Tests for `{{ cookiecutter.pkg_name }}` package."""

import logging 

import pytest
{% if cookiecutter.command_line_interface|lower == 'click' -%}
from click.testing import CliRunner

from {{ cookiecutter.pkg_name }}.cli_tools import cli
{%- endif %}

logger = logging.getLogger(__name__)


@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument.

    Arguments:
        response: pytest feature
    """
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string
    del response
{%- if cookiecutter.command_line_interface|lower == 'click' %}


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(cli.main)
    assert result.exit_code == 0
    assert '{{ cookiecutter.project_slug }}' in result.output
    help_result = runner.invoke(cli.main, ['--help'])
    assert help_result.exit_code == 0
    assert '--help' in help_result.output
    assert 'Show this message and exit.' in help_result.output
{%- endif %}


def test_py_version():
    """Dummy test to print python version used by pytest."""
    import sys
    logger.info(f"in TEST: {sys.version}  -- {sys.version_info}")
    # if sys.version_info <= (3, 9, 18):
    #     # 3.9 OK
    #     assert True
    # else:
    #     # 3.10 FAIL
    #     assert False
