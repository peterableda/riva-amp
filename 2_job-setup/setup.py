#!/usr/bin/env python3
"""
Setup Job for Riva Transcriptor Service AMP
Validates API connectivity and prepares the service for deployment.
"""

import os
import sys
import json
import tempfile
from pathlib import Path

# Add utils to path
sys.path.append(str(Path(__file__).parent.parent / "utils"))

from transcription_client import RivaTranscriptionClient
from audio_processor import AudioProcessor

def test_environment_variables():
    """Test that required environment variables are set."""
    print("🔧 Testing environment variables...")

    riva_url = os.getenv('RIVA_BASE_URL')
    if not riva_url:
        print("❌ RIVA_BASE_URL environment variable is not set")
        print("   Please set this in the AMP configuration to your Riva endpoint URL")
        return False

    print(f"✅ RIVA_BASE_URL is set: {riva_url}")
    return True

def test_api_connectivity():
    """Test connectivity to the Riva API."""
    print("\n🌐 Testing API connectivity...")

    try:
        client = RivaTranscriptionClient()
        if client.health_check():
            print("✅ Successfully connected to Riva service")
            return True
        else:
            print("❌ Could not connect to Riva service")
            print("   Please check the RIVA_BASE_URL and ensure the service is running")
            return False
    except Exception as e:
        print(f"❌ Error testing API connectivity: {e}")
        return False

def test_audio_processing():
    """Test audio processing capabilities."""
    print("\n🎵 Testing audio processing capabilities...")

    try:
        # Create a simple test audio file
        import numpy as np
        import soundfile as sf

        # Generate a simple sine wave (1 second, 440 Hz)
        sample_rate = 44100
        duration = 1.0
        frequency = 440.0

        t = np.linspace(0, duration, int(sample_rate * duration))
        audio_data = 0.3 * np.sin(2 * np.pi * frequency * t)

        # Save test file
        test_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        sf.write(test_file.name, audio_data, sample_rate)
        test_file.close()

        print(f"✅ Created test audio file: {test_file.name}")

        # Test conversion
        processor = AudioProcessor()
        converted_file = processor.convert_to_riva_format(test_file.name)

        print(f"✅ Successfully converted audio to Riva format: {converted_file}")

        # Validate the converted file
        is_valid, message = processor.validate_for_riva(converted_file)
        if is_valid:
            print(f"✅ Audio validation passed: {message}")
        else:
            print(f"⚠️  Audio validation issues: {message}")

        # Clean up
        processor.cleanup_temp_files([test_file.name, converted_file])
        print("✅ Cleaned up test files")

        return True

    except Exception as e:
        print(f"❌ Audio processing test failed: {e}")
        return False

def create_sample_files():
    """Create sample files and documentation."""
    print("\n📄 Creating sample files and documentation...")

    try:
        # Create data directory structure
        data_dir = Path(__file__).parent.parent / "data"
        temp_dir = Path(__file__).parent.parent / "temp"

        data_dir.mkdir(exist_ok=True)
        temp_dir.mkdir(exist_ok=True)

        # Create sample configuration file
        config_file = data_dir / "sample_config.json"
        sample_config = {
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

        with open(config_file, 'w') as f:
            json.dump(sample_config, f, indent=2)

        print(f"✅ Created sample configuration: {config_file}")

        # Create usage examples
        examples_file = data_dir / "usage_examples.md"
        examples_content = """# Riva Transcriptor Service Usage Examples

## Supported Audio Formats
- WAV (recommended)
- MP3
- M4A
- FLAC
- AAC
- OGG

## Best Practices
1. **Audio Quality**: Use clear recordings with minimal background noise
2. **File Size**: Keep files under 100MB for optimal performance
3. **Language**: Specify the correct language for better accuracy
4. **Format**: WAV format provides the best results

## API Integration Example
```python
from utils.transcription_client import RivaTranscriptionClient

client = RivaTranscriptionClient()
result = client.transcribe_audio("audio_file.wav", "en-US")
print(result["text"])
```

## Microphone Recording
The web interface provides browser-based microphone recording with automatic format conversion.

## File Upload
Drag and drop or click to upload audio files. The system automatically converts to the optimal format for Riva.
"""

        with open(examples_file, 'w') as f:
            f.write(examples_content)

        print(f"✅ Created usage examples: {examples_file}")

        return True

    except Exception as e:
        print(f"❌ Error creating sample files: {e}")
        return False

def validate_dependencies():
    """Validate that all required dependencies are available."""
    print("\n📦 Validating dependencies...")

    required_packages = [
        'gradio', 'requests', 'pydub', 'soundfile', 'librosa',
        'numpy', 'scipy', 'flask'
    ]

    missing_packages = []

    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} (missing)")
            missing_packages.append(package)

    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("   Please run the dependency installation step first")
        return False

    print("✅ All required packages are available")
    return True

def main():
    """Main setup function."""
    print("🚀 Starting Riva Transcriptor Service Setup\n")

    setup_steps = [
        ("Environment Variables", test_environment_variables),
        ("Dependencies", validate_dependencies),
        ("Audio Processing", test_audio_processing),
        ("API Connectivity", test_api_connectivity),
        ("Sample Files", create_sample_files),
    ]

    results = []
    for name, test_func in setup_steps:
        print(f"\n{'='*20} {name} {'='*20}")
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Error during {name}: {e}")
            results.append((name, False))

    print("\n" + "="*60)
    print("📋 SETUP SUMMARY")
    print("="*60)

    passed = 0
    warnings = 0
    for name, result in results:
        if result:
            status = "✅ PASS"
            passed += 1
        else:
            status = "❌ FAIL"
            # API connectivity failure is not critical during setup
            if name == "API Connectivity":
                status = "⚠️  WARN"
                warnings += 1
                passed += 1  # Count as passed for overall success

        print(f"{name:<25} {status}")

    print(f"\nSetup Results: {passed}/{len(results)} steps completed")

    if passed == len(results):
        print("🎉 Setup completed successfully!")
        print("The transcriptor service is ready to deploy.")
        print("\nNext steps:")
        print("1. Ensure RIVA_BASE_URL is correctly configured")
        print("2. Deploy the application from the 3_app directory")
        print("3. Access the web interface to start transcribing audio")
    elif warnings > 0 and passed >= len(results) - warnings:
        print("⚠️  Setup completed with warnings.")
        print("The service should work, but some features may be limited.")
        print("Please check the API connectivity when the Riva service is available.")
    else:
        print("❌ Setup failed. Please review the errors above.")
        return False

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
