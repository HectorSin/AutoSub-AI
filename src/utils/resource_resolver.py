import sys
from pathlib import Path

def get_resource_path(relative_path: str) -> Path:
    """
    Get absolute path to resource, works for dev and for PyInstaller.
    
    Args:
        relative_path: Path relative to the project root.
        
    Returns:
        Absolute Path object.
    """
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller temp folder
        base_path = Path(sys._MEIPASS)
    else:
        # Dev mode: src/utils/resource_resolver.py -> ../../
        # Assuming this file is in src/utils/
        base_path = Path(__file__).parent.parent.parent.resolve()
    
    return base_path / relative_path
