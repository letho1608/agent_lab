# -*- coding: utf-8 -*-
"""Tests for basic framework imports."""
from __future__ import absolute_import

import pytest


class TestBasicImports:
    """Test basic framework imports."""

    def test_import_pupy(self):
        """Test can import pupy package."""
        import pupy
        assert pupy is not None

    def test_import_pupylib(self):
        """Test can import pupylib."""
        from pupy import pupylib
        assert pupylib is not None

    def test_import_modules(self):
        """Test can import modules package."""
        from pupy import modules
        assert modules is not None

    def test_import_network(self):
        """Test can import network package."""
        from pupy import network
        assert network is not None

    def test_import_agent(self):
        """Test can import agent package."""
        from pupy import agent
        assert agent is not None

    def test_import_cli(self):
        """Test can import CLI package."""
        from pupy import cli
        assert cli is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
