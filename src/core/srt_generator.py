import os
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class SRTGenerator:
    """
    Handles generation of SRT subtitle files.
    """
    
    @staticmethod
    def format_timestamp(seconds: float) -> str:
        """
        Convert seconds to SRT timestamp format (00:00:00,000).
        
        Args:
            seconds: Time in seconds.
            
        Returns:
            Formatted timestamp string.
        """
        millis = int((seconds - int(seconds)) * 1000)
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    @staticmethod
    def generate_srt(segments: List[Dict[str, Any]], output_path: str):
        """
        Generate SRT file from segments.
        
        Args:
            segments: List of segments with 'start', 'end', 'text'.
            output_path: Path to save the SRT file.
        """
        try:
            # Ensure output directory exists
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, "w", encoding="utf-8") as f:
                for i, segment in enumerate(segments, start=1):
                    start_time = SRTGenerator.format_timestamp(segment["start"])
                    end_time = SRTGenerator.format_timestamp(segment["end"])
                    text = segment["text"].strip()
                    
                    f.write(f"{i}\n")
                    f.write(f"{start_time} --> {end_time}\n")
                    f.write(f"{text}\n\n")
            
            logger.info(f"SRT file generated: {output_path}")
            
        except Exception as e:
            logger.error(f"Failed to generate SRT file: {e}")
            raise

    @staticmethod
    def generate_output_filename(source_path: str, output_dir: str) -> str:
        """
        Generate unique output filename.
        Pattern: {source_name}_{timestamp}.srt
        
        Args:
            source_path: Path to the source video file.
            output_dir: Directory to save the SRT file.
            
        Returns:
            Full path to the output SRT file.
        """
        source_path_obj = Path(source_path)
        stem = source_path_obj.stem
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{stem}_{timestamp}.srt"
        
        output_path = Path(output_dir) / filename
        
        # Ensure uniqueness (though timestamp usually suffices)
        counter = 1
        while output_path.exists():
            filename = f"{stem}_{timestamp}_{counter}.srt"
            output_path = Path(output_dir) / filename
            counter += 1
            
        return str(output_path)
