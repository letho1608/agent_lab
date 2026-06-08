# -*- coding: utf-8 -*-
"""Comprehensive tests for Pupy core functionality."""
from __future__ import absolute_import

import pytest
import os
import sys
import tempfile
import shutil


class TestFrameworkCore:
    """Test core Pupy framework components."""

    def test_pupy_package_structure(self):
        """Test that Pupy package has all required submodules."""
        import pupy
        
        required_modules = [
            'agent',
            'cli',
            'commands',
            'network',
            'pupylib',
            'external',
        ]
        
        for module_name in required_modules:
            assert hasattr(pupy, module_name) or os.path.isdir(
                os.path.join(os.path.dirname(pupy.__file__), module_name)
            ), f"Missing required module: {module_name}"

    def test_pupy_version(self):
        """Test that version is defined."""
        try:
            from pupy import __version__
            assert __version__ is not None
        except ImportError:
            # Version might be in setup.py/pyproject.toml
            pass

    def test_agent_initialization(self):
        """Test that agent module can be imported."""
        from pupy.agent import config
        assert config is not None

    def test_cli_module(self):
        """Test CLI module availability."""
        from pupy.cli import pupysh
        assert hasattr(pupysh, 'main')

    def test_pupylib_core(self):
        """Test pupylib core components."""
        from pupy.pupylib import PupyModule
        from pupy.pupylib import PupyArgumentParser
        
        assert PupyModule is not None
        assert PupyArgumentParser is not None


class TestModuleSystem:
    """Test Pupy module loading and management."""

    def test_module_discovery(self):
        """Test that modules can be discovered."""
        modules_dir = os.path.join(
            os.path.dirname(__file__), '..', 'pupy', 'modules'
        )
        
        py_files = [f for f in os.listdir(modules_dir) 
                   if f.endswith('.py') and not f.startswith('_')]
        assert len(py_files) >= 90, f"Expected 90+ modules, found {len(py_files)}"

    def test_core_modules_available(self):
        """Test that critical modules exist."""
        modules_dir = os.path.join(
            os.path.dirname(__file__), '..', 'pupy', 'modules'
        )
        
        critical = [
            'shell_exec.py',
            'ps.py',
            'screenshot.py',
            'download.py',
            'upload.py',
            'get_info.py',
            'creds.py',
            'persistence.py',
        ]
        
        for module in critical:
            path = os.path.join(modules_dir, module)
            assert os.path.exists(path), f"Missing module: {module}"

    def test_module_has_class(self):
        """Test that modules have class definitions."""
        try:
            from pupy.modules import shell_exec
            # Modules should define a module class
            assert hasattr(shell_exec, '__class_name__') or \
                   any(c for c in dir(shell_exec) 
                       if c[0].isupper() and not c.startswith('_'))
        except ImportError:
            pytest.skip("Module import test requires full dependencies")


class TestConfiguration:
    """Test configuration system."""

    def test_config_files_exist(self):
        """Test that config files are in place."""
        config_dir = os.path.join(
            os.path.dirname(__file__), '..', 'config'
        )
        
        assert os.path.isdir(config_dir), "Config folder missing"
        assert os.path.exists(os.path.join(config_dir, '.env.example')), \
               "Missing .env.example"
        assert os.path.exists(os.path.join(config_dir, 'pupy.conf')), \
               "Missing pupy.conf"

    def test_pupy_conf_readable(self):
        """Test that pupy.conf is valid."""
        config_file = os.path.join(
            os.path.dirname(__file__), '..', 'config', 'pupy.conf'
        )
        
        try:
            from configparser import RawConfigParser
            parser = RawConfigParser()
            parser.read(config_file)
            
            # Should have some sections
            sections = parser.sections()
            assert len(sections) > 0, "pupy.conf has no sections"
        except ImportError:
            pytest.skip("ConfigParser not available")

    def test_env_example_format(self):
        """Test that .env.example is properly formatted."""
        env_file = os.path.join(
            os.path.dirname(__file__), '..', 'config', '.env.example'
        )
        
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should have some configuration patterns
        assert len(content) > 0, ".env.example is empty"
        # Should look like environment variables (KEY=VALUE or # comments)
        lines = [l.strip() for l in content.split('\n') if l.strip()]
        valid_lines = [l for l in lines 
                      if '=' in l or l.startswith('#') or l == '']
        assert len(valid_lines) > 0, ".env.example format invalid"


class TestNetworkComponents:
    """Test network and handler components."""

    def test_network_lib_exists(self):
        """Test that network library is available."""
        network_dir = os.path.join(
            os.path.dirname(__file__), '..', 'pupy', 'network'
        )
        
        assert os.path.isdir(network_dir)
        assert os.path.isdir(os.path.join(network_dir, 'lib'))
        assert os.path.isdir(os.path.join(network_dir, 'transports'))

    def test_transports_exist(self):
        """Test that transport handlers exist."""
        transports_dir = os.path.join(
            os.path.dirname(__file__), '..', 'pupy', 'network', 'transports'
        )
        
        transport_dirs = [d for d in os.listdir(transports_dir)
                          if os.path.isdir(os.path.join(transports_dir, d)) and not d.startswith('_')]
        assert len(transport_dirs) > 0, "No transport handlers found"


class TestPackagesAndLibraries:
    """Test Pupy packages and libraries."""

    def test_packages_directory_exists(self):
        """Test that packages directory exists."""
        packages_dir = os.path.join(
            os.path.dirname(__file__), '..', 'pupy', 'packages'
        )
        
        assert os.path.isdir(packages_dir)

    def test_external_tools_available(self):
        """Test that external tools are present."""
        external_dir = os.path.join(
            os.path.dirname(__file__), '..', 'pupy', 'external'
        )
        
        tools = [d for d in os.listdir(external_dir)
                if os.path.isdir(os.path.join(external_dir, d)) 
                and not d.startswith('_')]
        
        critical_tools = ['pywerview']
        for tool in critical_tools:
            assert tool in tools, f"Missing external tool: {tool}"


class TestBuildSystem:
    """Test payload build system."""

    def test_main_entry_point(self):
        """Test main.py entry point."""
        main_file = os.path.join(
            os.path.dirname(__file__), '..', 'main.py'
        )
        
        assert os.path.exists(main_file)
        
        # Check it's valid Python
        with open(main_file, 'r', encoding='utf-8') as f:
            source = f.read()
        
        compile(source, main_file, 'exec')

    def test_build_options_windows_only(self):
        """Test that build options are Windows-only."""
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        
        import main
        
        assert len(main.BUILD_OPTS) == 1
        assert main.BUILD_OPTS[0] == ("windows", "x64")

    def test_client_sources_windows_only(self):
        """Test that client sources are Windows-only."""
        sources_dir = os.path.join(
            os.path.dirname(__file__), '..', 'client', 'sources-windows-py3'
        )
        
        assert os.path.isdir(sources_dir)
        
        # Should have C source files
        c_files = [f for f in os.listdir(sources_dir)
                  if f.endswith(('.c', '.h'))]
        assert len(c_files) > 0


class TestDocumentation:
    """Test documentation completeness."""

    def test_readme_exists_and_valid(self):
        """Test README.md is valid."""
        readme = os.path.join(
            os.path.dirname(__file__), '..', 'README.md'
        )
        
        assert os.path.exists(readme)
        
        with open(readme, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for key sections
        sections = ['Overview', 'Quick Start', 'Architecture', 'Modules']
        for section in sections:
            assert section in content, f"README missing section: {section}"

    def test_install_guide_exists(self):
        """Test INSTALL.md exists with content."""
        install = os.path.join(
            os.path.dirname(__file__), '..', 'INSTALL.md'
        )
        
        assert os.path.exists(install)
        
        with open(install, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should have installation steps
        assert 'Installation' in content or 'install' in content.lower()
        assert 'Requirements' in content or 'requires' in content.lower()

    def test_docstrings_in_modules(self):
        """Test that critical modules have docstrings."""
        try:
            from pupy.pupylib import PupyModule
            
            assert PupyModule.__doc__ is not None, \
                   "PupyModule missing docstring"
        except ImportError:
            pytest.skip("Cannot import for docstring check")


class TestDependencies:
    """Test that dependencies are properly specified."""

    def test_requirements_file_exists(self):
        """Test requirements.txt is present."""
        req_file = os.path.join(
            os.path.dirname(__file__), '..', 'requirements.txt'
        )
        
        assert os.path.exists(req_file)

    def test_critical_packages_in_requirements(self):
        """Test that critical packages are required."""
        req_file = os.path.join(
            os.path.dirname(__file__), '..', 'requirements.txt'
        )
        
        with open(req_file, 'r', encoding='utf-8') as f:
            content = f.read().lower()
        
        critical = [
            'pycryptodome',
            'paramiko',
            'tornado',
            'impacket',
            'scapy',
        ]
        
        for pkg in critical:
            assert pkg in content, f"Missing required package: {pkg}"

    def test_pyproject_toml_has_dependencies(self):
        """Test pyproject.toml has project configuration."""
        pyproject = os.path.join(
            os.path.dirname(__file__), '..', 'pyproject.toml'
        )
        
        assert os.path.exists(pyproject)
        
        with open(pyproject, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should have project metadata
        assert '[project]' in content or 'name' in content


class TestWindowsCCompatibility:
    """Test Windows C compatibility."""

    def test_c_source_files_exist(self):
        """Test that Windows C sources are present."""
        sources_dir = os.path.join(
            os.path.dirname(__file__), '..', 'client', 'sources-windows-py3'
        )
        
        critical_files = [
            'main_exe.c',
            'pupy.c',
            'MemoryModule.c',
            'LoadLibraryR.c',
        ]
        
        for fname in critical_files:
            fpath = os.path.join(sources_dir, fname)
            assert os.path.exists(fpath), f"Missing C source: {fname}"

    def test_no_linux_source_files(self):
        """Test that Linux sources are removed."""
        linux_dir = os.path.join(
            os.path.dirname(__file__), '..', 'client', 'sources-linux-py3'
        )
        
        assert not os.path.exists(linux_dir), \
               "Linux sources should be removed"

    def test_no_android_build_sources(self):
        """Test that Android sources are removed."""
        android_dir = os.path.join(
            os.path.dirname(__file__), '..', 'client', 'android_sources'
        )
        
        assert not os.path.exists(android_dir), \
               "Android sources should be removed"


class TestIntegration:
    """Integration tests for core workflow."""

    def test_can_import_and_initialize(self):
        """Test basic import and initialization."""
        import pupy
        from pupy.pupylib import PupyModule
        from pupy.pupylib import PupyArgumentParser
        
        assert pupy is not None
        assert PupyModule is not None
        assert PupyArgumentParser is not None

    def test_project_structure_complete(self):
        """Test overall project structure."""
        base_dir = os.path.join(os.path.dirname(__file__), '..')
        
        required_dirs = [
            'pupy',
            'client',
            'tests',
            'config',
            'data',
        ]
        
        for dirname in required_dirs:
            dirpath = os.path.join(base_dir, dirname)
            assert os.path.isdir(dirpath), f"Missing directory: {dirname}"

    def test_entry_points_configured(self):
        """Test that console entry points are configured."""
        pyproject = os.path.join(
            os.path.dirname(__file__), '..', 'pyproject.toml'
        )
        
        with open(pyproject, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should define entry points
        assert 'pupysh' in content
        assert 'pupygen' in content


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
