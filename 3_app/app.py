#!/usr/bin/env python3
"""
Riva Transcriptor Service - Main Application
Web interface for audio transcription with microphone recording and file upload.
"""

import os
import sys
import tempfile
import json
from pathlib import Path
from typing import Optional, Tuple
import logging
import gradio as gr

from utils import RivaTranscriptionClient, AudioProcessor

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TranscriptorApp:
    """Main application class for the Riva Transcriptor Service."""

    def __init__(self):
        """Initialize the transcriptor application."""
        self.client = None
        self.temp_files = []

        # Load configuration
        self.config = self._load_config()

        # Initialize client
        self._init_client()

    def _load_config(self) -> dict:
        """Load configuration from file or use defaults."""
        config_path = Path(__file__).parent.parent / "data" / "sample_config.json"

        default_config = {
            "default_language": "en-US",
            "supported_languages": [
                "en-US", "en-GB", "es-ES", "fr-FR", "de-DE",
                "it-IT", "pt-BR", "ja-JP", "ko-KR", "zh-CN"
            ],
            "max_file_size_mb": 100,
            "supported_formats": [".wav", ".mp3", ".m4a", ".flac", ".aac", ".ogg"],
            "audio_settings": {
                "target_sample_rate": 16000,
                "target_channels": 1,
                "target_bit_depth": 16
            }
        }

        try:
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)
                logger.info("Loaded configuration from file")
                return config
        except Exception as e:
            logger.warning(f"Could not load config file: {e}")

        logger.info("Using default configuration")
        return default_config

    def _init_client(self):
        """Initialize the Riva transcription client."""
        try:
            self.client = RivaTranscriptionClient()
            logger.info("Riva client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Riva client: {e}")
            self.client = None

    def transcribe_microphone(self, audio_data, language: str) -> Tuple[str, str]:
        """
        Transcribe audio from microphone recording.

        Args:
            audio_data: Audio data from Gradio microphone component.
            language: Language code for transcription.

        Returns:
            Tuple of (transcription_text, status_message).
        """
        if audio_data is None:
            return "", "❌ No audio recorded. Please record some audio first."

        if self.client is None:
            return "", "❌ Transcription service is not available. Please check configuration."

        try:
            # audio_data is a tuple (sample_rate, numpy_array) from Gradio
            sample_rate, audio_array = audio_data

            # Save the audio to a temporary file
            temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)

            import soundfile as sf
            sf.write(temp_file.name, audio_array, sample_rate)
            temp_file.close()

            self.temp_files.append(temp_file.name)

            logger.info(f"Recorded audio saved to: {temp_file.name}")

            # Convert to Riva format
            converted_file = AudioProcessor.convert_to_riva_format(temp_file.name)
            self.temp_files.append(converted_file)

            # Transcribe
            result = self.client.transcribe_audio(converted_file, language)

            # Extract text from result
            transcription = result.get('text', '')
            if not transcription:
                # Try other possible keys
                transcription = result.get('transcription', result.get('transcript', str(result)))

            # Clean up temp files
            AudioProcessor.cleanup_temp_files(self.temp_files)
            self.temp_files = []

            status = f"✅ Transcription completed successfully! Language: {language}"
            return transcription, status

        except Exception as e:
            logger.error(f"Microphone transcription failed: {e}")
            # Clean up temp files on error
            AudioProcessor.cleanup_temp_files(self.temp_files)
            self.temp_files = []
            return "", f"❌ Transcription failed: {str(e)}"

    def transcribe_file_upload(self, uploaded_file, language: str) -> Tuple[str, str]:
        """
        Transcribe uploaded audio file.

        Args:
            uploaded_file: Uploaded file from Gradio file component.
            language: Language code for transcription.

        Returns:
            Tuple of (transcription_text, status_message).
        """
        if uploaded_file is None:
            return "", "❌ No file uploaded. Please upload an audio file."

        if self.client is None:
            return "", "❌ Transcription service is not available. Please check configuration."

        try:
            file_path = uploaded_file.name
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)

            logger.info(f"Processing uploaded file: {file_path} ({file_size_mb:.1f} MB)")

            # Check file size
            if file_size_mb > self.config["max_file_size_mb"]:
                return "", f"❌ File too large ({file_size_mb:.1f} MB). Maximum size: {self.config['max_file_size_mb']} MB"

            # Check if format is supported
            if not AudioProcessor.is_supported_format(file_path):
                supported = ", ".join(self.config["supported_formats"])
                return "", f"❌ Unsupported file format. Supported formats: {supported}"

            # Validate and convert audio
            is_valid, validation_message = AudioProcessor.validate_for_riva(file_path)

            if is_valid:
                # File is already in correct format
                transcription_file = file_path
                conversion_status = "File format is already compatible"
            else:
                # Convert to Riva format
                logger.info(f"Converting file: {validation_message}")
                transcription_file = AudioProcessor.convert_to_riva_format(file_path)
                self.temp_files.append(transcription_file)
                conversion_status = "File converted to Riva-compatible format"

            # Get audio info for status
            audio_info = AudioProcessor.get_audio_info(transcription_file)
            duration = audio_info.get('duration', 0)

            # Transcribe
            logger.info(f"Starting transcription of {transcription_file}")
            result = self.client.transcribe_audio(transcription_file, language)

            # Extract text from result
            transcription = result.get('text', '')
            if not transcription:
                # Try other possible keys
                transcription = result.get('transcription', result.get('transcript', str(result)))

            # Clean up temp files
            AudioProcessor.cleanup_temp_files(self.temp_files)
            self.temp_files = []

            status = f"✅ Transcription completed successfully!\n"
            status += f"Language: {language}\n"
            status += f"Duration: {duration:.1f} seconds\n"
            status += f"Status: {conversion_status}"

            return transcription, status

        except Exception as e:
            logger.error(f"File transcription failed: {e}")
            # Clean up temp files on error
            AudioProcessor.cleanup_temp_files(self.temp_files)
            self.temp_files = []
            return "", f"❌ Transcription failed: {str(e)}"

    def translate_file_upload(self, uploaded_file, target_language: str) -> Tuple[str, str]:
        """
        Translate uploaded audio file.

        Args:
            uploaded_file: Uploaded file from Gradio file component.
            target_language: Target language code for translation.

        Returns:
            Tuple of (translation_text, status_message).
        """
        if uploaded_file is None:
            return "", "❌ No file uploaded. Please upload an audio file."

        if self.client is None:
            return "", "❌ Translation service is not available. Please check configuration."

        try:
            file_path = uploaded_file.name
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)

            logger.info(f"Processing uploaded file for translation: {file_path} ({file_size_mb:.1f} MB)")

            # Check file size
            if file_size_mb > self.config["max_file_size_mb"]:
                return "", f"❌ File too large ({file_size_mb:.1f} MB). Maximum size: {self.config['max_file_size_mb']} MB"

            # Check if format is supported
            if not AudioProcessor.is_supported_format(file_path):
                supported = ", ".join(self.config["supported_formats"])
                return "", f"❌ Unsupported file format. Supported formats: {supported}"

            # Convert to Riva format if needed
            is_valid, validation_message = AudioProcessor.validate_for_riva(file_path)

            if is_valid:
                translation_file = file_path
                conversion_status = "File format is already compatible"
            else:
                logger.info(f"Converting file: {validation_message}")
                translation_file = AudioProcessor.convert_to_riva_format(file_path)
                self.temp_files.append(translation_file)
                conversion_status = "File converted to Riva-compatible format"

            # Get audio info for status
            audio_info = AudioProcessor.get_audio_info(translation_file)
            duration = audio_info.get('duration', 0)

            # Translate
            logger.info(f"Starting translation of {translation_file}")
            result = self.client.translate_audio(translation_file, target_language)

            # Extract text from result
            translation = result.get('text', '')
            if not translation:
                # Try other possible keys
                translation = result.get('translation', result.get('transcript', str(result)))

            # Clean up temp files
            AudioProcessor.cleanup_temp_files(self.temp_files)
            self.temp_files = []

            status = f"✅ Translation completed successfully!\n"
            status += f"Target Language: {target_language}\n"
            status += f"Duration: {duration:.1f} seconds\n"
            status += f"Status: {conversion_status}"

            return translation, status

        except Exception as e:
            logger.error(f"File translation failed: {e}")
            # Clean up temp files on error
            AudioProcessor.cleanup_temp_files(self.temp_files)
            self.temp_files = []
            return "", f"❌ Translation failed: {str(e)}"

    def create_interface(self):
        """Create the Gradio interface."""

        # Custom CSS for better styling
        css = """
        .gradio-container {
            max-width: 1200px !important;
        }
        .tab-nav {
            margin-bottom: 20px;
        }
        .output-text {
            min-height: 100px;
        }
        .status-text {
            font-family: monospace;
            font-size: 12px;
        }
        """

        with gr.Blocks(css=css, title="Riva Transcriptor Service") as interface:

            gr.Markdown("""
            # 🎤 Riva Transcriptor Service

            Convert speech to text using NVIDIA Riva technology. Choose between real-time microphone recording or file upload.

            **Supported Audio Formats:** WAV, MP3, M4A, FLAC, AAC, OGG
            **Maximum File Size:** 100 MB
            **Supported Languages:** Multiple languages supported
            """)

            with gr.Tabs():

                # Microphone Recording Tab
                with gr.TabItem("🎤 Microphone Recording"):
                    gr.Markdown("### Record audio directly from your microphone")

                    with gr.Row():
                        with gr.Column(scale=1):
                            mic_audio = gr.Audio(
                                sources=["microphone"],
                                type="numpy",
                                label="Record Audio",
                                format="wav"
                            )

                            mic_language = gr.Dropdown(
                                choices=self.config["supported_languages"],
                                value=self.config["default_language"],
                                label="Language"
                            )

                            mic_transcribe_btn = gr.Button("🔤 Transcribe Recording", variant="primary")

                        with gr.Column(scale=2):
                            mic_transcription = gr.Textbox(
                                label="Transcription",
                                placeholder="Your transcription will appear here...",
                                lines=8,
                                elem_classes=["output-text"]
                            )

                            mic_status = gr.Textbox(
                                label="Status",
                                placeholder="Ready to transcribe...",
                                lines=3,
                                elem_classes=["status-text"]
                            )

                    mic_transcribe_btn.click(
                        self.transcribe_microphone,
                        inputs=[mic_audio, mic_language],
                        outputs=[mic_transcription, mic_status]
                    )

                # File Upload Tab
                with gr.TabItem("📁 File Upload"):
                    gr.Markdown("### Upload an audio file for transcription")

                    with gr.Row():
                        with gr.Column(scale=1):
                            file_upload = gr.File(
                                label="Upload Audio File",
                                file_types=["audio"],
                                file_count="single"
                            )

                            file_language = gr.Dropdown(
                                choices=self.config["supported_languages"],
                                value=self.config["default_language"],
                                label="Language"
                            )

                            with gr.Row():
                                file_transcribe_btn = gr.Button("🔤 Transcribe File", variant="primary")
                                file_translate_btn = gr.Button("🌐 Translate to English", variant="secondary")

                        with gr.Column(scale=2):
                            file_output = gr.Textbox(
                                label="Output",
                                placeholder="Your transcription/translation will appear here...",
                                lines=8,
                                elem_classes=["output-text"]
                            )

                            file_status = gr.Textbox(
                                label="Status",
                                placeholder="Ready to process files...",
                                lines=3,
                                elem_classes=["status-text"]
                            )

                    file_transcribe_btn.click(
                        self.transcribe_file_upload,
                        inputs=[file_upload, file_language],
                        outputs=[file_output, file_status]
                    )

                    file_translate_btn.click(
                        self.translate_file_upload,
                        inputs=[file_upload, gr.State("en")],  # Always translate to English
                        outputs=[file_output, file_status]
                    )

                # About Tab
                with gr.TabItem("ℹ️ About"):
                    gr.Markdown(f"""
                    ### About Riva Transcriptor Service

                    This application provides speech-to-text transcription using NVIDIA Riva technology.

                    **Features:**
                    - Real-time microphone recording and transcription
                    - File upload with support for multiple audio formats
                    - Multi-language support
                    - Automatic audio format conversion
                    - Translation capabilities

                    **Technical Details:**
                    - Audio is automatically converted to mono 16-bit WAV at 16kHz for optimal results
                    - Files are processed securely and deleted after transcription
                    - Maximum file size: {self.config["max_file_size_mb"]} MB

                    **Supported Languages:**
                    {', '.join(self.config["supported_languages"])}

                    **Powered by:** NVIDIA Riva • Cloudera Machine Learning
                    """)

        return interface

def main():
    """Main application entry point."""
    print("🚀 Starting Riva Transcriptor Service Application")

    # Initialize application
    app = TranscriptorApp()

    # Create interface
    interface = app.create_interface()

    # Launch the application
    port = int(os.getenv('CDSW_APP_PORT', 7860))

    print(f"🌐 Launching application on port {port}")

    interface.launch(
        server_name="0.0.0.0",
        server_port=port,
        show_error=True,
        quiet=False
    )

if __name__ == "__main__":
    main()
