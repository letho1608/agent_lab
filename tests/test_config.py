# -*- coding: utf-8 -*-
"""Tests for configuration and environment setup."""
from __future__ import absolute_import

import pytest
import os
import sys
import tempfile
import shutil


class TestEnvironmentSetup:
    """Test environment and setup validation."""

    def test_python_version_requirement(self):
        """Test Python version is 3.9+."""
        assert sys.version_info >= (3, 9), \
               f"Requires Python 3.9+, got {sys.version_info.major}.{sys.version_info.minor}"

    def test_project_root_valid(self):
        """Test project root structure."""
        root = os.path.join(os.path.dirname(__file__), '..')
        
        # Check essential files
        assert os.path.exists(os.path.join(root, 'pyproject.toml'))
        assert os.path.exists(os.path.join(root, 'README.md'))
        assert os.path.exists(os.path.join(root, 'main.py'))

    def test_pytest_configuration(self):
        """Test pytest.ini configuration."""
        pytest_ini = os.path.join(
            os.path.dirname(__file__), '..', 'pytest.ini'
        )
        
        assert os.path.exists(pytest_ini), "pytest.ini missing"
        
        with open(pytest_ini, 'r') as f:
            content = f.read()
        
        assert '[pytest]' in content or 'testpaths' in content


class TestConfigurationFiles:
    """Test all configuration files."""

    def test_config_folder_structure(self):
        """Test config folder organization."""
        config_dir = os.path.join(
            os.path.dirname(__file__), '..', 'config'
        )
        
        assert os.path.isdir(config_dir)
        
        files = os.listdir(config_dir)
        assert '.env.example' in files
        assert 'pupy.conf' in files

    def test_env_example_content(self):
        """Test .env.example has expected format."""
        env_file = os.path.join(
            os.path.dirname(__file__), '..', 'config', '.env.example'
        )
        
        with open(env_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Should have content
        assert len(lines) > 0
        
        # Should have comments or assignments
        has_content = any('=' in line or '#' in line 
                         for line in lines if line.strip())
        assert has_content

    def test_pupy_conf_sections(self):
        """Test pupy.conf has valid sections."""
        conf_file = os.path.join(
            os.path.dirname(__file__), '..', 'config', 'pupy.conf'
        )
        
        with open(conf_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should have configuration sections
        assert '[' in content and ']' in content


class TestPackagingConfiguration:
    """Test package configuration for installation."""

    def test_pyproject_toml_valid(self):
        """Test pyproject.toml is valid."""
        pyproject = os.path.join(
            os.path.dirname(__file__), '..', 'pyproject.toml'
        )
        
        with open(pyproject, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should have build-system
        assert '[build-system]' in content
        # Should have project metadata
        assert '[project]' in content

    def test_project_metadata_complete(self):
        """Test project metadata is complete."""
        pyproject = os.path.join(
            os.path.dirname(__file__), '..', 'pyproject.toml'
        )
        
        with open(pyproject, 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_fields = [
            'name',
            'version',
            'description',
            'requires-python',
            'dependencies',
        ]
        
        for field in required_fields:
            assert field in content, f"Missing metadata field: {field}"

    def test_python_version_specified(self):
        """Test Python version requirement is specified."""
        pyproject = os.path.join(
            os.path.dirname(__file__), '..', 'pyproject.toml'
        )
        
        with open(pyproject, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should require 3.9+
        assert '3.9' in content or '>=3.9' in content

    def test_entry_points_defined(self):
        """Test console entry points are defined."""
        pyproject = os.path.join(
            os.path.dirname(__file__), '..', 'pyproject.toml'
        )
        
        with open(pyproject, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert '[project.scripts]' in content
        assert 'pupysh' in content
        assert 'pupygen' in content

    def test_dependencies_specified(self):
        """Test dependencies are specified in pyproject.toml."""
        pyproject = os.path.join(
            os.path.dirname(__file__), '..', 'pyproject.toml'
        )
        
        with open(pyproject, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should list dependencies
        assert 'dependencies' in content
        assert '[project.optional-dependencies]' in content or 'extras_require' in content


class TestBuildConfiguration:
    """Test build system configuration."""

    def test_pyoxidizer_config_exists(self):
        """Test PyOxidizer configuration."""
        pyoxidizer_dir = os.path.join(
            os.path.dirname(__file__), '..', 'client', 'pyoxidizer-build'
        )
        
        assert os.path.isdir(pyoxidizer_dir)
        
        # Check for config files
        config_files = [f for f in os.listdir(pyoxidizer_dir)
                       if f.endswith(('.bzl', '.toml', 'requirements.txt'))]
        assert len(config_files) > 0

    def test_client_build_requirements(self):
        """Test client build requirements specified."""
        req_file = os.path.join(
            os.path.dirname(__file__), '..', 'client', 'requirements.txt'
        )
        
        if os.path.exists(req_file):
            with open(req_file, 'r') as f:
                content = f.read()
            
            assert len(content) > 0


class TestToolConfiguration:
    """Test development tool configuration."""

    def test_flake8_config(self):
        """Test flake8 linter config."""
        pyproject = os.path.join(
            os.path.dirname(__file__), '..', 'pyproject.toml'
        )
        
        with open(pyproject, 'r') as f:
            content = f.read()
        
        # Should have flake8 config
        assert '[tool.flake8]' in content

    def test_black_config(self):
        """Test Black formatter config."""
        pyproject = os.path.join(
            os.path.dirname(__file__), '..', 'pyproject.toml'
        )
        
        with open(pyproject, 'r') as f:
            content = f.read()
        
        assert '[tool.black]' in content

    def test_ruff_config(self):
        """Test Ruff linter config."""
        pyproject = os.path.join(
            os.path.dirname(__file__), '..', 'pyproject.toml'
        )
        
        with open(pyproject, 'r') as f:
            content = f.read()
        
        assert '[tool.ruff]' in content

    def test_mypy_config(self):
        """Test MyPy type checker config."""
        pyproject = os.path.join(
            os.path.dirname(__file__), '..', 'pyproject.toml'
        )
        
        with open(pyproject, 'r') as f:
            content = f.read()
        
        assert '[tool.mypy]' in content


class TestConfigurationVariants:
    """Test different configuration scenarios."""

    def test_local_development_config(self):
        """Test local development configuration."""
        env_file = os.path.join(
            os.path.dirname(__file__), '..', 'config', '.env.example'
        )
        
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should have localhost examples
        assert '127.0.0.1' in content or 'localhost' in content

    def test_c2_server_config_defaults(self):
        """Test C2 server has configuration defaults."""
        conf_file = os.path.join(
            os.path.dirname(__file__), '..', 'config', 'pupy.conf'
        )
        
        with open(conf_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should have server section
        assert '[' in content


class TestConfigurationUsage:
    """Test configuration can be used correctly."""

    def test_config_can_be_copied(self):
        """Test that config files can be safely copied."""
        config_dir = os.path.join(
            os.path.dirname(__file__), '..', 'config'
        )
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Copy config files
            for fname in ['.env.example', 'pupy.conf']:
                src = os.path.join(config_dir, fname)
                dst = os.path.join(tmpdir, fname)
                shutil.copy2(src, dst)
                
                assert os.path.exists(dst)

    def test_startup_config_accessible(self):
        """Test that config is accessible from startup."""
        main_file = os.path.join(
            os.path.dirname(__file__), '..', 'main.py'
        )
        
        with open(main_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should reference config directory or files
        assert 'config' in content.lower() or 'conf' in content.lower()


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
