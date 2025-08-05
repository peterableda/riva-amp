# Riva Transcriptor Service

A Cloudera Applied Machine Learning Prototype (AMP) for audio transcription using NVIDIA Riva technology. This service provides a comprehensive web interface for speech-to-text conversion with both real-time microphone recording and file upload capabilities.

![Riva Transcriptor Service](images/transcriptor-banner.png)

## Features

### 🎤 Real-time Microphone Recording
- Browser-based audio recording
- Instant transcription feedback
- Multiple language support
- Automatic audio format optimization

### 📁 File Upload Transcription
- Drag-and-drop file upload interface
- Support for multiple audio formats (WAV, MP3, M4A, FLAC, AAC, OGG)
- Automatic format conversion to Riva-compatible format
- Batch processing capabilities

### 🌐 Translation Support
- Audio-to-text translation
- Multiple target languages
- High-quality translation powered by NVIDIA Riva

### 🔧 Technical Features
- Automatic audio format conversion (Mono, 16-bit, 16kHz WAV)
- Secure file handling with automatic cleanup
- JWT-based authentication with backend services
- Environment variable configuration
- Comprehensive error handling and validation

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Interface │    │   Transcriptor   │    │   NVIDIA Riva   │
│   (Gradio UI)   │───▶│    Service       │───▶│    Backend      │
│                 │    │   (Python API)   │    │   (REST API)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
        │                        │                        │
        ▼                        ▼                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Audio Recording │    │ Format Conversion│    │  Speech-to-Text │
│ & File Upload   │    │ & Validation     │    │  & Translation  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Requirements

### CML Environment
- **Runtime**: JupyterLab - Python 3.10 - Standard
- **Resources**:
  - Sessions: 2 CPU, 4GB Memory
  - Application: 2 CPU, 8GB Memory
- **Storage**: 10GB (for temporary audio file processing)

### External Dependencies
- **NVIDIA Riva Service**: A running Riva ASR (Automatic Speech Recognition) endpoint
- **Network Access**: Connectivity to Riva service and package repositories

### Environment Variables
- `RIVA_BASE_URL`: Base URL for your NVIDIA Riva service endpoint (required)

## Installation

### 1. Deploy as Cloudera AMP

1. Navigate to the **Prototype Catalog** in your CML workspace
2. Search for "Riva Transcriptor Service"
3. Click **"Launch as Project"**
4. Configure the required environment variables
5. Click **"Configure Project"**

### 2. Manual Installation

```bash
# Clone the repository
git clone <repository-url>
cd riva-transcriptor-service

# Set environment variables
export RIVA_BASE_URL="https://your-riva-endpoint.com/v1"

# Run the setup steps
python 1_session-install-deps/install.py
python 2_job-setup/setup.py

# Launch the application
cd 3_app
python app.py
```

## Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `RIVA_BASE_URL` | Base URL for NVIDIA Riva service | Yes | None |
| `CDSW_APP_PORT` | Port for the web application | No | 7860 |

### Audio Configuration

The service automatically converts audio to the following Riva-compatible format:

- **Sample Rate**: 16,000 Hz
- **Channels**: Mono (1 channel)
- **Bit Depth**: 16-bit
- **Format**: WAV (PCM)

### Supported Input Formats

- WAV (recommended)
- MP3
- M4A
- FLAC
- AAC
- OGG
- WebM (audio)

## Usage

### Web Interface

1. **Access the Application**: Navigate to the deployed application URL
2. **Choose Input Method**:
   - **Microphone**: Click the microphone tab for real-time recording
   - **File Upload**: Use the file upload tab for existing audio files

### Microphone Recording

1. Click the **"Record Audio"** button
2. Allow microphone permissions when prompted
3. Speak clearly into your microphone
4. Click **"Stop Recording"** when finished
5. Select the appropriate language
6. Click **"Transcribe Recording"** to get results

### File Upload

1. Drag and drop an audio file or click to browse
2. Select the audio language
3. Choose between:
   - **"Transcribe File"**: Convert speech to text in the same language
   - **"Translate to English"**: Translate speech to English text

### API Integration

You can also integrate directly with the transcription client:

```python
from utils.transcription_client import RivaTranscriptionClient

# Initialize client
client = RivaTranscriptionClient()

# Transcribe audio file
result = client.transcribe_audio("audio_file.wav", "en-US")
print(result["text"])

# Translate audio file
result = client.translate_audio("audio_file.wav", "en")
print(result["text"])
```

## Supported Languages

The service supports multiple languages for transcription:

- English (US, GB)
- Spanish (Spain)
- French (France)
- German (Germany)
- Italian (Italy)
- Portuguese (Brazil)
- Japanese
- Korean
- Chinese (Mandarin)

*Note: Available languages depend on your Riva service configuration.*

## Project Structure

```
riva-transcriptor-service/
├── 1_session-install-deps/      # Dependency installation
│   └── install.py
├── 2_job-setup/                 # Service setup and validation
│   └── setup.py
├── 3_app/                       # Main application
│   └── app.py
├── utils/                       # Utility modules
│   ├── transcription_client.py  # Riva API client
│   └── audio_processor.py       # Audio conversion utilities
├── data/                        # Data and configuration files
├── images/                      # Application screenshots
├── .project-metadata.yaml       # AMP metadata
├── catalog-entry.yaml          # AMP catalog information
├── requirements.txt            # Python dependencies
├── cdsw-build.sh              # Build script
└── README.md                  # This file
```

## Troubleshooting

### Common Issues

#### 1. "RIVA_BASE_URL environment variable is not set"
**Solution**: Set the `RIVA_BASE_URL` environment variable in your AMP configuration or export it in your shell.

#### 2. "Could not connect to Riva service"
**Solutions**:
- Verify the Riva service is running and accessible
- Check network connectivity to the Riva endpoint
- Validate the RIVA_BASE_URL format (should include `/v1` suffix)
- Ensure JWT token is available at `/tmp/jwt`

#### 3. "Audio conversion failed"
**Solutions**:
- Ensure ffmpeg is installed (handled by `cdsw-build.sh`)
- Check if the audio file is corrupted
- Verify the file format is supported
- Try with a smaller audio file

#### 4. "Microphone not working"
**Solutions**:
- Allow microphone permissions in your browser
- Check browser compatibility (Chrome/Firefox recommended)
- Ensure HTTPS is enabled for microphone access
- Test with a different browser or device

### File Size Limits

- **Maximum file size**: 100 MB
- **Recommended duration**: Under 10 minutes for optimal performance
- **Minimum duration**: 0.1 seconds

### Performance Tips

1. **Audio Quality**: Use clear recordings with minimal background noise
2. **File Format**: WAV format provides the best results
3. **Internet Connection**: Stable connection required for file uploads
4. **Language Selection**: Specify the correct language for better accuracy

## Development

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run setup
python 1_session-install-deps/install.py

# Start the application
cd 3_app
python app.py
```

### Testing

```bash
# Test API connectivity
python -c "from utils import RivaTranscriptionClient; print('Utils import successful')"

# Test audio processing
python -c "from utils import AudioProcessor; print('Audio processor import successful')"
```

## Integration Example

Here's a complete example of integrating with the Riva service:

```python
import os
from utils import RivaTranscriptionClient, AudioProcessor

# Set environment variables
os.environ['RIVA_BASE_URL'] = 'https://your-riva-endpoint.com/v1'

# Initialize components
client = RivaTranscriptionClient()
processor = AudioProcessor()

# Process and transcribe audio file
def transcribe_audio_file(file_path, language="en-US"):
    try:
        # Convert to Riva format
        converted_path = processor.convert_to_riva_format(file_path)

        # Transcribe
        result = client.transcribe_audio(converted_path, language)

        # Clean up
        processor.cleanup_temp_files([converted_path])

        return result.get('text', '')

    except Exception as e:
        print(f"Transcription failed: {e}")
        return None

# Usage
transcription = transcribe_audio_file("sample.mp3", "en-US")
print(f"Transcription: {transcription}")
```

## License

Copyright (c) 2024 Cloudera, Inc. All rights reserved.

This project is licensed under the Apache License 2.0. See the LICENSE file for details.

## Support

For support and questions:

1. Check the troubleshooting section above
2. Review the AMP deployment logs
3. Contact your Cloudera administrator
4. File issues in the project repository

## Contributing

This is a Cloudera AMP designed for demonstration and educational purposes. For contributions or enhancements, please follow your organization's development guidelines.

---

**Powered by:** NVIDIA Riva • Cloudera Machine Learning • Python • Gradio
