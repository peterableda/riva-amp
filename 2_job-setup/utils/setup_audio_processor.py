"""
Minimal Audio Processor for Setup/Testing
Only includes basic functionality needed for setup validation.
"""

import os
import tempfile
import logging
from pathlib import Path
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

class SetupAudioProcessor:
    """Minimal audio processor for setup testing."""

    TARGET_SAMPLE_RATE = 16000
    TARGET_CHANNELS = 1

    def convert_to_riva_format(self, input_path: str, output_path: str = None) -> str:
        """
        Minimal conversion - just copy the file for testing purposes.
        In setup, we're only testing the flow, not actual conversion.
        """
        try:
            import soundfile as sf
            import numpy as np

            # Read the input file
            data, sample_rate = sf.read(input_path)

            # Simple conversion logic for testing
            if len(data.shape) > 1:
                # Convert to mono by taking the first channel
                data = data[:, 0]

            # Create output path if not provided
            if output_path is None:
                output_path = tempfile.NamedTemporaryFile(suffix='.wav', delete=False).name

            # Write in target format
            sf.write(output_path, data, self.TARGET_SAMPLE_RATE)

            logger.info(f"Test conversion completed: {input_path} -> {output_path}")
            return output_path

        except ImportError:
            logger.warning("soundfile not available, creating dummy output for testing")
            # Create a dummy file for testing when dependencies aren't available
            if output_path is None:
                output_path = tempfile.NamedTemporaryFile(suffix='.wav', delete=False).name

            # Copy input to output for basic testing
            import shutil
            shutil.copy2(input_path, output_path)
            return output_path

        except Exception as e:
            logger.error(f"Conversion failed: {e}")
            raise

    def validate_for_riva(self, file_path: str) -> Tuple[bool, str]:
        """
        Basic validation for testing.
        """
        try:
            if not os.path.exists(file_path):
                return False, "File does not exist"

            file_size = os.path.getsize(file_path)
            if file_size == 0:
                return False, "File is empty"

            # Basic file extension check
            if not file_path.lower().endswith(('.wav', '.mp3', '.flac', '.m4a')):
                return False, "Unsupported file format"

            return True, f"Basic validation passed (file size: {file_size} bytes)"

        except Exception as e:
            return False, f"Validation error: {e}"

    def cleanup_temp_files(self, file_paths: list):
        """Clean up temporary files created during testing."""
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    os.unlink(file_path)
                    logger.info(f"Cleaned up: {file_path}")
            except Exception as e:
                logger.warning(f"Could not clean up {file_path}: {e}")
