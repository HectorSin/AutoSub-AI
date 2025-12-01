import sys
import os
from pathlib import Path
import shutil
from unittest.mock import MagicMock, patch

# Add src to path
sys.path.append(os.getcwd())

from src.core.audio_processor import AudioProcessor

def test_audio_processor():
    print("Testing AudioProcessor...")
    tmp_path = Path("temp_test_audio")
    tmp_path.mkdir(exist_ok=True)
    
    try:
        ap = AudioProcessor(temp_dir=str(tmp_path))
        
        # Test validate
        video_file = tmp_path / "test.mp4"
        video_file.touch()
        assert ap.validate_video_file(str(video_file)) is True
        print("validate_video_file PASS")
        
        # Test extract
        with patch("src.core.audio_processor.ffmpeg") as mock_ffmpeg:
            mock_stream = MagicMock()
            mock_ffmpeg.input.return_value = mock_stream
            mock_stream.output.return_value = mock_stream
            
            output = ap.extract_audio(str(video_file))
            assert output.endswith(".mp3")
            print("extract_audio PASS")
            
    except Exception as e:
        print(f"FAIL: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if tmp_path.exists():
            shutil.rmtree(tmp_path)

if __name__ == "__main__":
    test_audio_processor()
