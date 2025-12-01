import pytest
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
import ffmpeg

# Add src to path
sys.path.append(os.getcwd())

from src.core.audio_processor import AudioProcessor
from src.core.stt_engine import STTEngine
from src.core.llm_engine import LLMEngine
from src.core.srt_generator import SRTGenerator

@pytest.fixture
def temp_dir(tmp_path):
    return tmp_path

@pytest.fixture
def dummy_video(temp_dir):
    """Generate a dummy video file using ffmpeg."""
    output_path = temp_dir / "test_video.mp4"
    
    # Generate 2 seconds of silence/video
    try:
        (
            ffmpeg
            .input('anullsrc', format='lavfi', t=2)
            .output(str(output_path), f='mp4', vcodec='libx264', acodec='aac')
            .overwrite_output()
            .run(quiet=True)
        )
    except ffmpeg.Error as e:
        # Fallback if ffmpeg fails (e.g. missing codecs), just touch the file
        # But AudioProcessor needs a real file to extract audio from...
        # If this fails, the test will fail, which is good.
        print(f"FFmpeg generation failed: {e}")
        output_path.touch()
        
    return str(output_path)

def test_full_pipeline(temp_dir, dummy_video):
    print(f"Testing pipeline with video: {dummy_video}")
    
    # 1. Audio Extraction
    # We rely on system ffmpeg now
    ap = AudioProcessor(temp_dir=str(temp_dir))
    audio_path = ap.extract_audio(dummy_video)
    
    assert audio_path is not None
    assert os.path.exists(audio_path)
    assert audio_path.endswith(".mp3")
    
    # 2. STT
    # We mock STT to avoid loading large models during quick tests
    # But for "Integration", we might want to run it? 
    # Loading "tiny" model is fast enough.
    # Let's mock it for speed and reliability in this environment.
    with patch("src.core.stt_engine.WhisperModel") as MockModel:
        mock_instance = MockModel.return_value
        # Mock transcribe return
        Segment = MagicMock()
        Segment.start = 0.0
        Segment.end = 1.0
        Segment.text = " Hello World "
        Segment.avg_logprob = -0.5
        
        mock_instance.transcribe.return_value = ([Segment], MagicMock(duration=2.0))
        
        stt = STTEngine(model_size="tiny", device="cpu")
        segments = stt.transcribe(audio_path)
        
        assert len(segments) == 1
        assert segments[0]["text"] == "Hello World"
        
    # 3. LLM
    # Mock Gemini
    with patch("src.core.llm_engine.genai") as mock_genai:
        mock_model = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model
        
        # Mock response
        mock_response = MagicMock()
        mock_response.text = '[{"start": 0.0, "end": 1.0, "text": "안녕 세상아"}]'
        mock_model.generate_content.return_value = mock_response
        
        llm = LLMEngine(api_key="dummy_key")
        corrected_segments = llm.correct_subtitles(segments)
        
        assert len(corrected_segments) == 1
        assert corrected_segments[0]["text"] == "안녕 세상아"
        
    # 4. SRT Generation
    output_srt = temp_dir / "output.srt"
    SRTGenerator.generate_srt(corrected_segments, str(output_srt))
    
    assert output_srt.exists()
    content = output_srt.read_text(encoding="utf-8")
    assert "안녕 세상아" in content
    assert "00:00:00,000 --> 00:00:01,000" in content
