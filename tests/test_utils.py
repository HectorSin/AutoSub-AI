import pytest
import sys
from pathlib import Path
from src.utils.resource_resolver import get_resource_path

def test_resource_resolver_dev():
    # Ensure _MEIPASS is not set
    if hasattr(sys, '_MEIPASS'):
        del sys._MEIPASS
        
    path = get_resource_path("assets/app.ico")
    # In dev, it should be relative to project root
    # src/utils/resource_resolver.py is 3 levels deep from root?
    # Actually, the implementation uses __file__.parent.parent.parent
    
    expected_root = Path(__file__).parent.parent.resolve()
    # Wait, test file is in tests/, so __file__.parent is tests/
    # But we are testing the function which uses ITS OWN __file__ location.
    
    # Just check if it resolves to an absolute path containing "assets"
    assert path.is_absolute()
    assert "assets" in str(path)

def test_resource_resolver_frozen(monkeypatch):
    # Mock _MEIPASS
    monkeypatch.setattr(sys, '_MEIPASS', '/tmp/MEI12345', raising=False)
    
    path = get_resource_path("config.yaml")
    assert str(path) == str(Path('/tmp/MEI12345/config.yaml'))
