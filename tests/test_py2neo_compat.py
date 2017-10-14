#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `py2neo_compat` package."""

from __future__ import absolute_import, print_function

import pytest


from py2neo_compat import py2neo_compat


@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument."""
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string
