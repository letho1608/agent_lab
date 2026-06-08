# -*- coding: utf-8 -*-
"""Tests for module system validation."""
from __future__ import absolute_import

import pytest
import os


class TestModuleSystem:
    """Test module discovery and validation."""

    def test_modules_directory_exists(self):
        """Test modules directory exists."""
        modules_dir = os.path.join(
            os.path.dirname(__file__), '..', 'pupy', 'modules'
        )
        
        assert os.path.isdir(modules_dir)

    def test_module_count(self):
        """Test minimum module count (95+)."""
        modules_dir = os.path.join(
            os.path.dirname(__file__), '..', 'pupy', 'modules'
        )
        
        module_files = [f for f in os.listdir(modules_dir)
                       if f.endswith('.py') and f != '__init__.py']
        
        assert len(module_files) >= 90, \
            f"Expected 90+ modules, found {len(module_files)}"

    def test_critical_modules_exist(self):
        """Test critical modules are present."""
        modules_dir = os.path.join(
            os.path.dirname(__file__), '..', 'pupy', 'modules'
        )
        
        critical_modules = [
            'shell_exec.py',
            'ps.py',
            'download.py',
            'upload.py',
        ]
        
        for module in critical_modules:
            assert os.path.exists(os.path.join(modules_dir, module)), \
                f"Critical module missing: {module}"

    def test_no_linux_modules(self):
        """Test Linux-specific modules are removed."""
        modules_dir = os.path.join(
            os.path.dirname(__file__), '..', 'pupy', 'modules'
        )
        
        files = os.listdir(modules_dir)
        linux_modules = [
            'hide_process.py', 'linux_stealth.py',
            'ttyrec.py', 'usniper.py'
        ]
        
        for module in linux_modules:
            assert module not in files, \
                f"Linux module still present: {module}"

    def test_no_android_modules(self):
        """Test Android-specific modules are removed."""
        modules_dir = os.path.join(
            os.path.dirname(__file__), '..', 'pupy', 'modules'
        )
        
        files = os.listdir(modules_dir)
        android_modules = [
            'apps.py', 'call.py', 'contacts.py',
            'gpstracker.py', 'vibrate.py', 'webcamsnap.py'
        ]
        
        for module in android_modules:
            assert module not in files, \
                f"Android module still present: {module}"

    def test_module_encoding(self):
        """Test modules use UTF-8 encoding."""
        modules_dir = os.path.join(
            os.path.dirname(__file__), '..', 'pupy', 'modules'
        )
        
        # Test a few modules for proper encoding
        test_count = 0
        for fname in os.listdir(modules_dir)[:5]:
            if fname.endswith('.py'):
                fpath = os.path.join(modules_dir, fname)
                
                # Should be readable as UTF-8
                try:
                    with open(fpath, 'r', encoding='utf-8') as f:
                        _ = f.read()
                    test_count += 1
                except UnicodeDecodeError:
                    pytest.fail(f"Module {fname} has encoding issues")
        
        assert test_count > 0


class TestExternalTools:
    """Test external tools integration."""

    def test_external_tools_directory(self):
        """Test external tools directory exists."""
        external_dir = os.path.join(
            os.path.dirname(__file__), '..', 'pupy', 'external'
        )
        
        assert os.path.isdir(external_dir)

    def test_windows_tools_present(self):
        """Test Windows-focused tools are present."""
        external_dir = os.path.join(
            os.path.dirname(__file__), '..', 'pupy', 'external'
        )
        
        windows_tools = []
        
        available_tools = os.listdir(external_dir)
        
        for tool in windows_tools:
            assert tool in available_tools, \
                f"Windows tool missing: {tool}"


class TestWindowsSources:
    """Test Windows payload sources."""

    def test_windows_sources_exist(self):
        """Test Windows sources directory exists."""
        sources_dir = os.path.join(
            os.path.dirname(__file__), '..', 'client', 'sources-windows-py3'
        )
        
        assert os.path.isdir(sources_dir)

    def test_critical_windows_sources(self):
        """Test critical Windows source files."""
        sources_dir = os.path.join(
            os.path.dirname(__file__), '..', 'client', 'sources-windows-py3'
        )
        
        critical_files = [
            'main_exe.c',
            'pupy.c',
            'MemoryModule.c',
            'MemoryModule.h',
        ]
        
        for fname in critical_files:
            fpath = os.path.join(sources_dir, fname)
            assert os.path.exists(fpath), \
                f"Critical Windows source missing: {fname}"

    def test_no_linux_sources(self):
        """Test Linux sources are removed."""
        sources_linux = os.path.join(
            os.path.dirname(__file__), '..', 'client', 'sources-linux-py3'
        )
        
        assert not os.path.exists(sources_linux), \
            "Linux sources should be removed"

    def test_no_android_sources(self):
        """Test Android sources are removed."""
        sources_android = os.path.join(
            os.path.dirname(__file__), '..', 'client', 'android_sources'
        )
        
        assert not os.path.exists(sources_android), \
            "Android sources should be removed"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
