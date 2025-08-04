#!/usr/bin/env python3
"""
Environment Validation Script for Riva Transcriptor Service AMP
Validates that the CML environment meets requirements for running the transcriptor service.
"""

import sys
import os
import subprocess
import json
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} is not compatible. Python 3.8+ required.")
        return False

def check_environment_variables():
    """Check if required environment variables are set."""
    print("\n🔧 Checking environment variables...")

    # Check if RIVA_BASE_URL is set
    riva_url = os.getenv('RIVA_BASE_URL')
    if riva_url:
        print(f"✅ RIVA_BASE_URL is set: {riva_url}")
    else:
        print("⚠️  RIVA_BASE_URL is not set. This should be configured in the AMP settings.")

    return True

def check_jwt_token():
    """Check if JWT token file exists."""
    print("\n🔑 Checking JWT token availability...")

    jwt_path = "/tmp/jwt"
    if os.path.exists(jwt_path):
        try:
            with open(jwt_path, 'r') as f:
                token_data = json.load(f)
            if 'access_token' in token_data:
                print("✅ JWT token file found and contains access_token")
                return True
            else:
                print("❌ JWT token file exists but missing access_token")
                return False
        except json.JSONDecodeError:
            print("❌ JWT token file exists but contains invalid JSON")
            return False
    else:
        print("⚠️  JWT token file not found at /tmp/jwt. This is expected if running outside CML workbench.")
        return True

def check_system_capabilities():
    """Check system capabilities for audio processing."""
    print("\n🎵 Checking system capabilities...")

    # Check if ffmpeg is available (will be installed via cdsw-build.sh)
    try:
        result = subprocess.run(['which', 'ffmpeg'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ ffmpeg is available")
        else:
            print("ℹ️  ffmpeg not found (will be installed during build)")
    except Exception as e:
        print(f"ℹ️  Could not check ffmpeg: {e}")

    return True

def check_disk_space():
    """Check available disk space."""
    print("\n💾 Checking disk space...")

    try:
        result = subprocess.run(['df', '-h', '.'], capture_output=True, text=True)
        print("📊 Disk usage:")
        print(result.stdout)
        return True
    except Exception as e:
        print(f"❌ Could not check disk space: {e}")
        return False

def main():
    """Main validation function."""
    print("🚀 Starting Riva Transcriptor Service Environment Validation\n")

    checks = [
        ("Python Version", check_python_version),
        ("Environment Variables", check_environment_variables),
        ("JWT Token", check_jwt_token),
        ("System Capabilities", check_system_capabilities),
        ("Disk Space", check_disk_space),
    ]

    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Error during {name} check: {e}")
            results.append((name, False))

    print("\n" + "="*50)
    print("📋 VALIDATION SUMMARY")
    print("="*50)

    passed = 0
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name:<25} {status}")
        if result:
            passed += 1

    print(f"\nValidation Results: {passed}/{len(results)} checks passed")

    if passed == len(results):
        print("🎉 Environment validation completed successfully!")
        print("You can proceed with installing dependencies.")
    else:
        print("⚠️  Some validation checks failed. Please review the issues above.")
        print("You may still be able to proceed, but some functionality might be limited.")

    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
