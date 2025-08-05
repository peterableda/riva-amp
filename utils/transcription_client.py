"""
Transcription Client for NVIDIA Riva Service
Handles API communication with the Riva transcription endpoint.
"""

import os
import json
import requests
import logging
from pathlib import Path
from typing import Optional, Dict, Any

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RivaTranscriptionClient:
    """Client for communicating with NVIDIA Riva transcription service."""

    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        """
        Initialize the Riva transcription client.

        Args:
            base_url: Base URL for the Riva service. If None, reads from RIVA_BASE_URL env var.
            api_key: API key for authentication. If None, reads from JWT token file.
        """
        self.base_url = base_url or os.getenv('RIVA_BASE_URL')
        if not self.base_url:
            raise ValueError("RIVA_BASE_URL environment variable must be set or base_url provided")

        # Ensure base_url doesn't end with slash
        self.base_url = self.base_url.rstrip('/')

        # Get API key
        self.api_key = api_key or self._get_api_key()
        if not self.api_key:
            raise ValueError("Could not obtain API key. Ensure JWT token file exists or provide api_key")

        # Set up headers
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json"
        }

        logger.info(f"Initialized Riva client with base URL: {self.base_url}")

    def _get_api_key(self) -> Optional[str]:
        """
        Get API key from JWT token file.

        Returns:
            API key string or None if not found.
        """
        jwt_path = "/tmp/jwt"
        try:
            if os.path.exists(jwt_path):
                with open(jwt_path, 'r') as f:
                    token_data = json.load(f)
                return token_data.get("access_token")
            else:
                logger.warning(f"JWT token file not found at {jwt_path}")
                return None
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error reading JWT token file: {e}")
            return None

    def transcribe_audio(self, audio_file_path: str, language: str = "en-US") -> Dict[str, Any]:
        """
        Transcribe an audio file using the Riva service.

        Args:
            audio_file_path: Path to the audio file to transcribe.
            language: Language code for transcription (default: "en-US").

        Returns:
            Dictionary containing transcription results.

        Raises:
            requests.exceptions.RequestException: If API request fails.
            FileNotFoundError: If audio file doesn't exist.
        """
        if not os.path.exists(audio_file_path):
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

        url = f"{self.base_url}/audio/transcriptions"

        try:
            with open(audio_file_path, "rb") as audio_file:
                files = {"file": audio_file}
                data = {"language": language}

                logger.info(f"Sending transcription request for {audio_file_path}")
                response = requests.post(
                    url,
                    headers=self.headers,
                    files=files,
                    data=data,
                    timeout=300  # 5 minute timeout for large files
                )

                response.raise_for_status()
                result = response.json()

                logger.info("Transcription completed successfully")
                return result

        except requests.exceptions.RequestException as e:
            logger.error(f"Transcription request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response body: {e.response.text}")
            raise

    def translate_audio(self, audio_file_path: str, language: str = "en") -> Dict[str, Any]:
        """
        Translate an audio file using the Riva service.

        Args:
            audio_file_path: Path to the audio file to translate.
            language: Target language code for translation (default: "en").

        Returns:
            Dictionary containing translation results.

        Raises:
            requests.exceptions.RequestException: If API request fails.
            FileNotFoundError: If audio file doesn't exist.
        """
        if not os.path.exists(audio_file_path):
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

        url = f"{self.base_url}/audio/translations"

        try:
            with open(audio_file_path, "rb") as audio_file:
                files = {"file": audio_file}
                data = {"language": language}

                logger.info(f"Sending translation request for {audio_file_path}")
                response = requests.post(
                    url,
                    headers=self.headers,
                    files=files,
                    data=data,
                    timeout=300  # 5 minute timeout for large files
                )

                response.raise_for_status()
                result = response.json()

                logger.info("Translation completed successfully")
                return result

        except requests.exceptions.RequestException as e:
            logger.error(f"Translation request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response body: {e.response.text}")
            raise

    def health_check(self) -> bool:
        """
        Check if the Riva service is accessible.

        Returns:
            True if service is accessible, False otherwise.
        """
        try:
            # Try to access the base URL to check connectivity
            response = requests.get(
                self.base_url,
                headers=self.headers,
                timeout=30
            )
            # Don't require 200 status, just that we can connect
            logger.info(f"Health check response: {response.status_code}")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Health check failed: {e}")
            return False

# Convenience function for easy usage
def create_client() -> RivaTranscriptionClient:
    """
    Create a RivaTranscriptionClient using environment variables.

    Returns:
        Configured RivaTranscriptionClient instance.
    """
    return RivaTranscriptionClient()

# Example usage
if __name__ == "__main__":
    try:
        client = create_client()

        # Example transcription (commented out as it requires actual audio file)
        # result = client.transcribe_audio("sample.wav", "en-US")
        # print(json.dumps(result, indent=2))

        # Health check
        if client.health_check():
            print("✅ Riva service is accessible")
        else:
            print("❌ Riva service is not accessible")

    except Exception as e:
        print(f"❌ Error: {e}")
