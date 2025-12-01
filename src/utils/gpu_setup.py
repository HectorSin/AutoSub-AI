import os
import sys
import logging
from pathlib import Path

# Basic logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def add_nvidia_dll_path():
    """
    Add NVIDIA library paths to DLL search path for Windows.
    This is required for ctranslate2 to find cuDNN/cuBLAS DLLs installed via pip.
    """
    if sys.platform == "win32":
        try:
            import importlib.util
            
            libs = [
                ("nvidia.cudnn", "bin"),
                ("nvidia.cublas", "bin")
            ]
            
            for lib_name, sub_dir in libs:
                spec = importlib.util.find_spec(lib_name)
                if spec and spec.submodule_search_locations:
                    lib_path = Path(spec.submodule_search_locations[0])
                    dll_path = lib_path / sub_dir
                    
                    if dll_path.exists():
                        # Add to DLL search path (Python 3.8+)
                        os.add_dll_directory(str(dll_path))
                        
                        # Add to system PATH (for C++ dependencies like ctranslate2)
                        os.environ['PATH'] = str(dll_path) + os.pathsep + os.environ['PATH']
                        
                        logger.info(f"Added DLL directory to PATH: {dll_path}")
                    else:
                        logger.warning(f"DLL directory not found: {dll_path}")
                else:
                    logger.warning(f"Could not find spec for {lib_name}")
                
        except ImportError:
            logger.warning("NVIDIA libraries not found in python environment. GPU inference might fail.")
        except Exception as e:
            logger.error(f"Failed to add NVIDIA DLL paths: {e}")

if __name__ == "__main__":
    add_nvidia_dll_path()
