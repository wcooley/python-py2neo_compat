#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

import tomli

if __name__ == '__main__':
    # This is probably pretty fragile
    with open('pyproject.toml', 'rb') as inp:
        pyproject = tomli.load(inp)

    setup(
        name=pyproject['project']['name'],
        version='1.0.0',
        license=pyproject['project']['license']['text'],
        description=pyproject['project']['description'],
        packages=find_packages(where='src/', include=['*']),
        package_dir={'': 'src'},
        py_modules=[
        ],
        install_requires=pyproject['project']['dependencies'],
        extras_require=pyproject['project']['optional-dependencies'],
    )
