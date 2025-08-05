"""
Utils package for Riva Transcriptor Service
Contains audio processing and transcription client utilities.
"""

# Import classes only when accessed to avoid dependency issues
def __getattr__(name):
    if name == 'AudioProcessor':
        from .audio_processor import AudioProcessor
        return AudioProcessor
    elif name == 'RivaTranscriptionClient':
        from .transcription_client import RivaTranscriptionClient
        return RivaTranscriptionClient
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

__all__ = ['AudioProcessor', 'RivaTranscriptionClient']
