#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for :mod:`py2neo_compat.util`."""

from __future__ import absolute_import, print_function

import os
import sys

import pytest  # noqa


@pytest.mark.parametrize(
    ('name', 'ns', 'result'), [
        ('ShortName', '.sub.BiggerName',    ('py2neo.sub', 'BiggerName')),
        ('ShortName', '.sub.',              ('py2neo.sub', 'ShortName')),
        ('ShortName', '.sub.sub2.',         ('py2neo.sub.sub2', 'ShortName')),
        ('ShortName', 'top.sub.',           ('top.sub', 'ShortName')),
        ('ShortName', 'top.sub.BiggerName', ('top.sub', 'BiggerName')),
    ]
)
def test_qualify_symbol(name, ns, result):
    """Test :func:`resolve_symbol`."""

    from py2neo_compat.util import qualify_symbol

    assert qualify_symbol(name, ns) == result


@pytest.mark.parametrize(
    ('modname', 'symname', 'result'), [
        ('sys', 'path', sys.path),
        ('os', 'path', os.path),
    ]
)
def test_import_symbol(modname, symname, result):
    """Test :func:`import_symbol`."""
    from py2neo_compat.util import import_symbol

    assert import_symbol(modname, symname) == result
