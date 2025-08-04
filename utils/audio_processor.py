"""
Audio Processing Utilities for Riva Transcriptor Service
Handles audio format conversion and validation.
"""

import os
import tempfile
import logging
from pathlib import Path
from typing import Optional, Tuple
import soundfile as sf
import numpy as np
from pydub import AudioSegment
from pydub.utils import which

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check if ffmpeg is available
AudioSegment.converter = which("ffmpeg")
AudioSegment.ffmpeg = which("ffmpeg")
AudioSegment.ffprobe = which("ffprobe")

class AudioProcessor:
    """Handles audio file processing and format conversion."""

    # Supported input formats
    SUPPORTED_FORMATS = {'.wav', '.mp3', '.m4a', '.flac', '.aac', '.ogg', '.webm'}

    # Target format for Riva (Mono, 16-bit, 16kHz)
    TARGET_SAMPLE_RATE = 16000
    TARGET_CHANNELS = 1
    TARGET_BIT_DEPTH = 16

    @classmethod
    def is_supported_format(cls, file_path: str) -> bool:
        """
        Check if the file format is supported.

        Args:
            file_path: Path to the audio file.

        Returns:
            True if format is supported, False otherwise.
        """
        suffix = Path(file_path).suffix.lower()
        return suffix in cls.SUPPORTED_FORMATS

    @classmethod
    def get_audio_info(cls, file_path: str) -> dict:
        """
        Get information about an audio file.

        Args:
            file_path: Path to the audio file.

        Returns:
            Dictionary with audio file information.
        """
        try:
            with sf.SoundFile(file_path) as f:
                return {
                    'sample_rate': f.samplerate,
                    'channels': f.channels,
                    'frames': f.frames,
                    'duration': f.frames / f.samplerate,
                    'format': f.format,
                    'subtype': f.subtype
                }
        except Exception as e:
            logger.error(f"Error reading audio file info: {e}")
            # Fallback to pydub
            try:
                audio = AudioSegment.from_file(file_path)
                return {
                    'sample_rate': audio.frame_rate,
                    'channels': audio.channels,
                    'frames': len(audio.get_array_of_samples()),
                    'duration': len(audio) / 1000.0,  # pydub uses milliseconds
                    'format': 'unknown',
                    'subtype': 'unknown'
                }
            except Exception as e2:
                logger.error(f"Error reading audio file with pydub: {e2}")
                return {}

    @classmethod
    def convert_to_riva_format(cls, input_path: str, output_path: Optional[str] = None) -> str:
        """
        Convert audio file to Riva-compatible format (Mono, 16-bit, 16kHz WAV).

        Args:
            input_path: Path to the input audio file.
            output_path: Path for the output file. If None, creates temp file.

        Returns:
            Path to the converted audio file.

        Raises:
            ValueError: If input file is not supported.
            RuntimeError: If conversion fails.
        """
        if not cls.is_supported_format(input_path):
            raise ValueError(f"Unsupported audio format: {Path(input_path).suffix}")

        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input audio file not found: {input_path}")

        # Create output path if not provided
        if output_path is None:
            temp_dir = tempfile.gettempdir()
            output_path = os.path.join(temp_dir, f"converted_{os.path.basename(input_path)}.wav")

        try:
            logger.info(f"Converting {input_path} to Riva format...")

            # First try with soundfile (faster for supported formats)
            try:
                data, sample_rate = sf.read(input_path)

                # Convert to mono if stereo
                if len(data.shape) > 1 and data.shape[1] > 1:
                    data = np.mean(data, axis=1)

                # Resample if necessary
                if sample_rate != cls.TARGET_SAMPLE_RATE:
                    import scipy.signal
                    num_samples = int(len(data) * cls.TARGET_SAMPLE_RATE / sample_rate)
                    data = scipy.signal.resample(data, num_samples)

                # Ensure data is in the right range for 16-bit
                if data.dtype != np.int16:
                    # Normalize to [-1, 1] then convert to int16
                    if data.dtype in [np.float32, np.float64]:
                        data = np.clip(data, -1.0, 1.0)
                        data = (data * 32767).astype(np.int16)
                    else:
                        data = data.astype(np.int16)

                # Write the converted file
                sf.write(output_path, data, cls.TARGET_SAMPLE_RATE, subtype='PCM_16')

            except Exception as e:
                logger.warning(f"soundfile conversion failed, trying pydub: {e}")

                # Fallback to pydub
                audio = AudioSegment.from_file(input_path)

                # Convert to mono
                if audio.channels > 1:
                    audio = audio.set_channels(1)

                # Convert to target sample rate
                if audio.frame_rate != cls.TARGET_SAMPLE_RATE:
                    audio = audio.set_frame_rate(cls.TARGET_SAMPLE_RATE)

                # Ensure 16-bit
                audio = audio.set_sample_width(2)  # 2 bytes = 16 bits

                # Export as WAV
                audio.export(output_path, format="wav")

            # Verify the conversion
            info = cls.get_audio_info(output_path)
            logger.info(f"Conversion successful. Output: {info}")

            if info.get('sample_rate') != cls.TARGET_SAMPLE_RATE:
                logger.warning(f"Sample rate mismatch: expected {cls.TARGET_SAMPLE_RATE}, got {info.get('sample_rate')}")

            if info.get('channels') != cls.TARGET_CHANNELS:
                logger.warning(f"Channel mismatch: expected {cls.TARGET_CHANNELS}, got {info.get('channels')}")

            return output_path

        except Exception as e:
            logger.error(f"Audio conversion failed: {e}")
            raise RuntimeError(f"Failed to convert audio file: {e}")

    @classmethod
    def validate_for_riva(cls, file_path: str) -> Tuple[bool, str]:
        """
        Validate if an audio file is compatible with Riva service.

        Args:
            file_path: Path to the audio file.

        Returns:
            Tuple of (is_valid, message).
        """
        try:
            info = cls.get_audio_info(file_path)

            if not info:
                return False, "Could not read audio file information"

            issues = []

            # Check sample rate
            if info.get('sample_rate') != cls.TARGET_SAMPLE_RATE:
                issues.append(f"Sample rate should be {cls.TARGET_SAMPLE_RATE}Hz (got {info.get('sample_rate')}Hz)")

            # Check channels
            if info.get('channels') != cls.TARGET_CHANNELS:
                issues.append(f"Should be mono (got {info.get('channels')} channels)")

            # Check duration (reasonable limits)
            duration = info.get('duration', 0)
            if duration > 600:  # 10 minutes
                issues.append(f"File too long ({duration:.1f}s). Consider splitting into smaller segments.")

            if duration < 0.1:  # 100ms
                issues.append(f"File too short ({duration:.3f}s)")

            if issues:
                return False, "Issues found: " + "; ".join(issues)
            else:
                return True, "Audio file is compatible with Riva service"

        except Exception as e:
            return False, f"Error validating audio file: {e}"

    @classmethod
    def cleanup_temp_files(cls, file_paths: list):
        """
        Clean up temporary audio files.

        Args:
            file_paths: List of file paths to delete.
        """
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"Cleaned up temporary file: {file_path}")
            except Exception as e:
                logger.error(f"Error cleaning up file {file_path}: {e}")

# Convenience functions
def convert_audio_for_riva(input_path: str, output_path: Optional[str] = None) -> str:
    """Convert audio file to Riva format."""
    return AudioProcessor.convert_to_riva_format(input_path, output_path)

def validate_audio_for_riva(file_path: str) -> Tuple[bool, str]:
    """Validate audio file for Riva compatibility."""
    return AudioProcessor.validate_for_riva(file_path)

# Example usage
if __name__ == "__main__":
    # Example usage (commented out)
    # processor = AudioProcessor()
    # converted_path = processor.convert_to_riva_format("input.mp3")
    # is_valid, message = processor.validate_for_riva(converted_path)
    # print(f"Valid: {is_valid}, Message: {message}")
    pass
