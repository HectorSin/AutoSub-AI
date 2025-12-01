import sys
import os
from pathlib import Path
import shutil

# Add src to path
sys.path.append(os.getcwd())

from tests.test_srt_generator import test_format_timestamp, test_generate_srt, test_generate_output_filename
from src.core.srt_generator import SRTGenerator

class MockPath:
    def __init__(self, path):
        self.path = Path(path)
    
    def __truediv__(self, other):
        return MockPath(self.path / other)
    
    def __str__(self):
        return str(self.path)
    
    def exists(self):
        return self.path.exists()
        
    def read_text(self, encoding=None):
        return self.path.read_text(encoding=encoding)

def run_tests():
    print("Running test_format_timestamp...")
    try:
        test_format_timestamp()
        print("PASS")
    except Exception as e:
        print(f"FAIL: {e}")

    print("Running test_generate_srt...")
    try:
        # Create temp dir
        tmp_path = Path("temp_test")
        tmp_path.mkdir(exist_ok=True)
        test_generate_srt(tmp_path)
        print("PASS")
    except Exception as e:
        print(f"FAIL: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if Path("temp_test").exists():
            shutil.rmtree("temp_test")

    print("Running test_generate_output_filename...")
    try:
        tmp_path = Path("temp_test_2")
        tmp_path.mkdir(exist_ok=True)
        test_generate_output_filename(tmp_path)
        print("PASS")
    except Exception as e:
        print(f"FAIL: {e}")
    finally:
        if Path("temp_test_2").exists():
            shutil.rmtree("temp_test_2")

if __name__ == "__main__":
    run_tests()
