
"""Tests for :mod:`py2neo_compat.util`."""

import pytest
from py2neo_compat import Node
from py2neo_compat.util import foremost


@pytest.mark.unit
def test_foremost():
    assert foremost([False]) == False
    assert foremost([True]) == True
    assert foremost([None], default=object()) is not None

    n = Node()
    assert bool(n) is False and foremost([n]) is n
