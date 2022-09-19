"""Console script for {{cookiecutter.pkg_name}}."""

{% if cookiecutter.command_line_interface|lower == 'click' -%}
import click
from {{ cookiecutter.pkg_name }} import __version__


@click.command()
def main():
    """Main entrypoint."""
    _str = f"{{ cookiecutter.project_slug }} v{__version__}"
    click.echo(_str)
    click.echo("=" * len("_str"))
    click.echo("{{ cookiecutter.project_short_description }}")


if __name__ == "__main__":
    main()  # pragma: no cover
{%- endif %}
