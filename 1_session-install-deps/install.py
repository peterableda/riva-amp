#!/usr/bin/env python3
"""
Dependencies Installation Script for Riva Transcriptor Service AMP
Installs all required Python packages and validates the installation.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True,
                              capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout.strip():
            print(f"Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"Error: {e.stderr}")
        return False

def install_system_dependencies():
    """Install system-level dependencies."""
    print("\n📦 Installing system dependencies...")

    commands = [
        ("apt-get update", "Updating package lists"),
        ("apt-get install -y ffmpeg libsndfile1 libsndfile1-dev portaudio19-dev python3-pyaudio",
         "Installing audio processing libraries"),
    ]

    for command, description in commands:
        if not run_command(command, description):
            return False

    return True

def install_python_dependencies():
    """Install Python dependencies from requirements.txt."""
    print("\n🐍 Installing Python dependencies...")

    # First upgrade pip
    if not run_command("pip install --upgrade pip", "Upgrading pip"):
        print("⚠️  Failed to upgrade pip, continuing anyway...")

    # Install requirements
    requirements_path = Path(__file__).parent.parent / "requirements.txt"
    if requirements_path.exists():
        command = f"pip install -r {requirements_path}"
        return run_command(command, "Installing Python packages from requirements.txt")
    else:
        print(f"❌ Requirements file not found at {requirements_path}")
        return False

def validate_installations():
    """Validate that key packages are installed correctly."""
    print("\n🔍 Validating installations...")

    packages_to_check = [
        "gradio",
        "requests",
        "pydub",
        "soundfile",
        "librosa",
        "numpy",
        "scipy",
        "flask"
    ]

    failed_packages = []

    for package in packages_to_check:
        try:
            __import__(package)
            print(f"✅ {package} imported successfully")
        except ImportError as e:
            print(f"❌ {package} import failed: {e}")
            failed_packages.append(package)

    if failed_packages:
        print(f"\n⚠️  The following packages failed to import: {', '.join(failed_packages)}")
        return False
    else:
        print(f"\n✅ All {len(packages_to_check)} packages validated successfully!")
        return True

def create_sample_data():
    """Create sample data directory structure."""
    print("\n📁 Setting up data directories...")

    data_dir = Path(__file__).parent.parent / "data"
    temp_dir = Path(__file__).parent.parent / "temp"

    try:
        data_dir.mkdir(exist_ok=True)
        temp_dir.mkdir(exist_ok=True)

        # Create a readme file in data directory
        readme_path = data_dir / "README.md"
        with open(readme_path, 'w') as f:
            f.write("""# Data Directory

This directory is used for storing uploaded audio files and temporary processing files.

## Structure
- Upload audio files will be temporarily stored here for processing
- The directory will be cleaned up automatically after transcription
- Supported formats: WAV, MP3, M4A, FLAC (converted to WAV for processing)

## Notes
- Files are automatically deleted after processing for security
- Maximum file size recommended: 100MB
- For best results, use clear audio recordings
""")

        print("✅ Data directories created successfully")
        return True

    except Exception as e:
        print(f"❌ Failed to create data directories: {e}")
        return False

def main():
    """Main installation function."""
    print("🚀 Starting Riva Transcriptor Service Dependencies Installation\n")

    # Check if running as root or with sufficient privileges
    if os.geteuid() != 0:
        print("⚠️  Not running as root. System dependency installation may fail.")
        print("If you encounter permission errors, you may need to run with sudo.")

    installation_steps = [
        ("System Dependencies", install_system_dependencies),
        ("Python Dependencies", install_python_dependencies),
        ("Installation Validation", validate_installations),
        ("Data Directory Setup", create_sample_data),
    ]

    results = []
    for name, install_func in installation_steps:
        try:
            result = install_func()
            results.append((name, result))
            if not result:
                print(f"⚠️  {name} failed, but continuing with remaining steps...")
        except Exception as e:
            print(f"❌ Error during {name}: {e}")
            results.append((name, False))

    print("\n" + "="*50)
    print("📋 INSTALLATION SUMMARY")
    print("="*50)

    passed = 0
    for name, result in results:
        status = "✅ SUCCESS" if result else "❌ FAILED"
        print(f"{name:<25} {status}")
        if result:
            passed += 1

    print(f"\nInstallation Results: {passed}/{len(results)} steps completed successfully")

    if passed == len(results):
        print("🎉 All dependencies installed successfully!")
        print("You can now proceed to set up the transcriptor service.")
    else:
        print("⚠️  Some installation steps failed. Please review the errors above.")
        print("You may still be able to run the service with limited functionality.")

    return passed >= len(results) - 1  # Allow for one failure

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
