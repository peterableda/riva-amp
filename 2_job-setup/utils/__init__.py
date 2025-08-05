"""
Minimal utils package for setup/testing purposes
Contains simplified versions with reduced dependencies.
"""

# Import classes only when accessed to avoid dependency issues
def __getattr__(name):
    if name == 'AudioProcessor':
        from .setup_audio_processor import SetupAudioProcessor
        return SetupAudioProcessor
    elif name == 'RivaTranscriptionClient':
        from .setup_transcription_client import SetupTranscriptionClient
        return SetupTranscriptionClient
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

__all__ = ['RivaTranscriptionClient', 'AudioProcessor']
