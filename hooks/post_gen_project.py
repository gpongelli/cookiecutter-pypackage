#!/usr/bin/env python
import os
import subprocess
import sys
import shutil

PROJECT_DIRECTORY = os.path.realpath(os.path.curdir)


def remove_file(filepath):
    try:
        os.remove(os.path.join(PROJECT_DIRECTORY, filepath))
    except FileNotFoundError:
        pass


def remove_folder(folder_path):
    try:
        shutil.rmtree(os.path.join(PROJECT_DIRECTORY, folder_path), ignore_errors=True)
    except FileNotFoundError:
        pass


def rename_folder(folder_name, dest_name):
    try:
        shutil.move(os.path.join(PROJECT_DIRECTORY, folder_name),
                    os.path.join(PROJECT_DIRECTORY, dest_name))
    except FileNotFoundError:
        pass


def execute(list_args, supress_exception=False, cwd=None):
    cur_dir = os.getcwd()

    try:
        if cwd:
            os.chdir(cwd)

        proc = subprocess.run(list_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if proc.returncode != 0 and not supress_exception:
            raise Exception(proc)
        else:
            return proc
    finally:
        os.chdir(cur_dir)


def init_git():
    # workaround for issue #1
    if not os.path.exists(os.path.join(PROJECT_DIRECTORY, ".git")):
        execute(["git", "config", "--global", "init.defaultBranch", "main"], cwd=PROJECT_DIRECTORY)
        execute(["git", "init"], cwd=PROJECT_DIRECTORY)


def install_pre_commit_hooks():
    execute([sys.executable, "-m", "pip", "install", "pre-commit==2.12.0"], cwd=PROJECT_DIRECTORY)
    execute([sys.executable, "-m", "pre_commit", "install"], cwd=PROJECT_DIRECTORY)


if __name__ == '__main__':

    if 'mkdocstr' in '{{ cookiecutter.doc_generator|lower }}':
        # remove sphinx
        for remove_me in ['AUTHORS.rst', 'CONTRIBUTING.rst']:
            remove_file(remove_me)
        remove_folder('sphinx_docs')
        rename_folder('mkdocstring_docs', 'docs')
    else:
        # remove mkdocstring
        for remove_me in ['CONTRIBUTING.md', 'mkdocs.yml']:
            remove_file(remove_me)
        remove_folder('mkdocstring_docs')
        rename_folder('sphinx_docs', 'docs')

    if 'no' in '{{ cookiecutter.command_line_interface|lower }}':
        cli_file = os.path.join('{{ cookiecutter.pkg_name }}', 'cli.py')
        remove_file(cli_file)

    if 'Not open source' == '{{ cookiecutter.open_source_license }}':
        remove_file('LICENSE')

    try:
        init_git()
    except Exception as e:
        print(e)

    if '{{ cookiecutter.install_precommit_hooks }}' == 'y':
        try:
            install_pre_commit_hooks()
        except Exception as e:
            print(str(e))
            print("Failed to install pre-commit hooks. Please run `pre-commit install` by your self. For more on pre-commit, please refer to https://pre-commit.com")
