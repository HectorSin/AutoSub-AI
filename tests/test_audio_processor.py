import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from src.core.audio_processor import AudioProcessor

@pytest.fixture
def audio_processor(tmp_path):
    return AudioProcessor(temp_dir=str(tmp_path))

def test_validate_video_file(audio_processor, tmp_path):
    # Create dummy video file
    video_file = tmp_path / "test.mp4"
    video_file.touch()
    
    assert audio_processor.validate_video_file(str(video_file)) is True
    
    # Test invalid extension
    txt_file = tmp_path / "test.txt"
    txt_file.touch()
    assert audio_processor.validate_video_file(str(txt_file)) is False
    
    # Test non-existent file
    assert audio_processor.validate_video_file(str(tmp_path / "missing.mp4")) is False

@patch("src.core.audio_processor.ffmpeg")
def test_extract_audio(mock_ffmpeg, audio_processor, tmp_path):
    video_file = tmp_path / "test.mp4"
    video_file.touch()
    
    # Mock ffmpeg.input().output().run()
    mock_stream = MagicMock()
    mock_ffmpeg.input.return_value = mock_stream
    mock_stream.output.return_value = mock_stream
    
    output_path = audio_processor.extract_audio(str(video_file))
    
    assert output_path.endswith(".mp3")
    assert Path(output_path).parent == audio_processor.temp_dir
    
    # Verify ffmpeg calls
    mock_ffmpeg.input.assert_called_with(str(video_file))
    mock_ffmpeg.run.assert_called_once()
