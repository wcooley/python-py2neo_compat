#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from __future__ import absolute_import, print_function

import os
from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

# Enable setting version higher for testing
PY2NEO_MAX_VERSION = os.environ.get('PY2NEO_MAX_VERSION', '2')

requirements = [
    'boltons',
    'py2neo>=1.6,<={}.999'.format(PY2NEO_MAX_VERSION),
    'six',
    'typing',
]

setup_requirements = [
    'setuptools_scm',
]

test_requirements = [
    'coverage',
    'pytest >= 3.3.0',
    'pytest-cov',
    'pytest-forked',
    'pytest-mock',
]

setup(
    name='py2neo_compat',
    version='0.1.0',
    use_scm_version=True,
    description="Compatibility layer for py2neo",
    long_description=readme + '\n\n' + history,
    long_description_content_type='text/x-rst',
    author="Wil Cooley",
    author_email='wcooley@nakedape.cc',
    url='https://github.com/wcooley/py2neo_compat',
    package_dir={'': 'src',},
    packages=find_packages(where='src', include=['py2neo_compat']),
    include_package_data=True,
    install_requires=requirements,
    license="Apache Software License 2.0",
    zip_safe=False,
    keywords='py2neo_compat py2neo compat neo4j',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    extras_require={
        'test': test_requirements,
    },
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
