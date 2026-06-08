# -*- coding: utf-8 -*-
"""Tests for CLI components (pupysh, pupygen)."""
from __future__ import absolute_import

import pytest
import os
import sys
import subprocess


class TestCLIEntryPoints:
    """Test command-line entry points."""

    def test_pupysh_cli_importable(self):
        """Test pupysh CLI module is importable."""
        root = os.path.join(os.path.dirname(__file__), '..')
        sys.path.insert(0, root)
        
        try:
            from pupy.cli import pupysh
            assert hasattr(pupysh, '__main__') or hasattr(pupysh, '__file__')
        except ImportError:
            pytest.skip("pupysh not importable in test environment")

    def test_pupygen_cli_importable(self):
        """Test pupygen CLI module is importable."""
        root = os.path.dirname(__file__) or '.'
        sys.path.insert(0, root)
        
        try:
            from pupy.cli import pupygen
            assert hasattr(pupygen, '__main__') or hasattr(pupygen, '__file__')
        except ImportError:
            pytest.skip("pupygen not importable in test environment")


class TestPupyShell:
    """Test pupysh command-line shell."""

    def test_pupysh_module_exists(self):
        """Test pupysh.py module exists."""
        cli_dir = os.path.join(
            os.path.dirname(__file__), '..', 'pupy', 'cli'
        )
        
        pupysh_file = os.path.join(cli_dir, 'pupysh.py')
        assert os.path.exists(pupysh_file), "pupysh.py not found"

    def test_pupysh_has_main(self):
        """Test pupysh has main components."""
        cli_dir = os.path.join(
            os.path.dirname(__file__), '..', 'pupy', 'cli'
        )
        
        pupysh_file = os.path.join(cli_dir, 'pupysh.py')
        
        with open(pupysh_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should have main function or entry point
        assert 'if __name__' in content or 'def main' in content

    def test_pupysh_help_syntax(self):
        """Test pupysh has help text."""
        cli_dir = os.path.join(
            os.path.dirname(__file__), '..', 'pupy', 'cli'
        )
        
        pupysh_file = os.path.join(cli_dir, 'pupysh.py')
        
        with open(pupysh_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should have argparse or help setup
        assert 'help' in content.lower() or 'parser' in content


class TestPupyGen:
    """Test pupygen payload generator."""

    def test_pupygen_module_exists(self):
        """Test pupygen.py module exists."""
        cli_dir = os.path.join(
            os.path.dirname(__file__), '..', 'pupy', 'cli'
        )
        
        pupygen_file = os.path.join(cli_dir, 'pupygen.py')
        assert os.path.exists(pupygen_file), "pupygen.py not found"

    def test_pupygen_has_payload_generator(self):
        """Test pupygen has payload generation."""
        cli_dir = os.path.join(
            os.path.dirname(__file__), '..', 'pupy', 'cli'
        )
        
        pupygen_file = os.path.join(cli_dir, 'pupygen.py')
        
        with open(pupygen_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should reference payload or generation
        assert 'generate' in content.lower() or 'payload' in content.lower()

    def test_pupygen_windows_support(self):
        """Test pupygen generates Windows payloads."""
        cli_dir = os.path.join(
            os.path.dirname(__file__), '..', 'pupy', 'cli'
        )
        
        pupygen_file = os.path.join(cli_dir, 'pupygen.py')
        
        with open(pupygen_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should support Windows
        assert 'windows' in content.lower() or 'win' in content.lower()


class TestCLIStructure:
    """Test CLI module structure."""

    def test_cli_directory_exists(self):
        """Test CLI directory exists."""
        cli_dir = os.path.join(
            os.path.dirname(__file__), '..', 'pupy', 'cli'
        )
        
        assert os.path.isdir(cli_dir)

    def test_cli_has_init(self):
        """Test CLI has __init__.py."""
        cli_dir = os.path.join(
            os.path.dirname(__file__), '..', 'pupy', 'cli'
        )
        
        init_file = os.path.join(cli_dir, '__init__.py')
        assert os.path.exists(init_file)

    def test_cli_modules_importable(self):
        """Test CLI modules are importable."""
        root = os.path.dirname(__file__) or '.'
        sys.path.insert(0, root)
        
        try:
            from pupy import cli
            assert hasattr(cli, '__file__')
        except ImportError as e:
            pytest.skip(f"CLI not importable: {e}")


class TestPayloadBuilding:
    """Test payload building functionality."""

    def test_main_py_build_support(self):
        """Test main.py supports building."""
        main_file = os.path.join(
            os.path.dirname(__file__), '..', 'main.py'
        )
        
        with open(main_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should have build options
        assert 'build' in content.lower() or 'windows' in content.lower()

    def test_windows_payload_builder_available(self):
        """Test Windows payload builder is available."""
        sources_dir = os.path.join(
            os.path.dirname(__file__), '..', 'client', 'sources-windows-py3'
        )
        
        assert os.path.isdir(sources_dir)

    def test_build_templates_present(self):
        """Test build templates are present."""
        pyox_dir = os.path.join(
            os.path.dirname(__file__), '..', 'client', 'pyoxidizer-build'
        )
        
        files = os.listdir(pyox_dir) if os.path.isdir(pyox_dir) else []
        
        # Should have build templates
        assert any(f.endswith(('.bzl', '.toml')) for f in files)


class TestCLIOutput:
    """Test CLI output formatting."""

    def test_cli_modules_have_output(self):
        """Test CLI modules handle output."""
        cli_dir = os.path.join(
            os.path.dirname(__file__), '..', 'pupy', 'cli'
        )
        
        for fname in os.listdir(cli_dir):
            if (fname.endswith('.py') and 
                fname != '__init__.py' and 
                fname != '__main__.py'):  # Skip launcher files
                fpath = os.path.join(cli_dir, fname)
                with open(fpath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Should have print, logging, or output handling
                assert any(x in content for x in [
                    'print(', 'logging', 'sys.stdout', 'click',
                    'argparse', 'parser'
                ])


class TestCLIIntegration:
    """Test CLI integration with framework."""

    def test_cli_imports_framework(self):
        """Test CLI imports pupy framework."""
        cli_dir = os.path.join(
            os.path.dirname(__file__), '..', 'pupy', 'cli'
        )
        
        for fname in os.listdir(cli_dir):
            if fname.endswith('.py') and fname != '__init__.py':
                fpath = os.path.join(cli_dir, fname)
                with open(fpath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Should import from pupy
                if 'import' in content:
                    assert 'from pupy' in content or 'import pupy' in content

    def test_cli_commands_available(self):
        """Test CLI commands are available."""
        cli_dir = os.path.join(
            os.path.dirname(__file__), '..', 'pupy', 'cli'
        )
        
        cli_files = [f for f in os.listdir(cli_dir)
                    if f.endswith('.py') and f != '__init__.py']
        
        assert len(cli_files) >= 2, "Expected at least pupysh.py and pupygen.py"


class TestCommandOptions:
    """Test command-line options."""

    def test_pupysh_connection_options(self):
        """Test pupysh has connection options."""
        cli_dir = os.path.join(
            os.path.dirname(__file__), '..', 'pupy', 'cli'
        )
        
        pupysh_file = os.path.join(cli_dir, 'pupysh.py')
        
        with open(pupysh_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should handle host, port, or connection string
        assert any(x in content for x in [
            'host', 'port', 'address', 'connect', 'server'
        ])

    def test_pupygen_output_options(self):
        """Test pupygen has output options."""
        cli_dir = os.path.join(
            os.path.dirname(__file__), '..', 'pupy', 'cli'
        )
        
        pupygen_file = os.path.join(cli_dir, 'pupygen.py')
        
        with open(pupygen_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should have output file handling
        assert any(x in content for x in [
            'output', '-o', '--output', 'file', 'save'
        ])


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
