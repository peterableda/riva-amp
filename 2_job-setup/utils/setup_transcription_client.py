"""
Minimal Transcription Client for Setup/Testing
Only includes connectivity testing functionality.
"""

import os
import requests
import logging

logger = logging.getLogger(__name__)

class SetupTranscriptionClient:
    """Minimal client for setup testing - only health check functionality."""

    def __init__(self, base_url: str = None):
        """Initialize with minimal setup for testing."""
        self.base_url = base_url or os.getenv('RIVA_BASE_URL')
        if not self.base_url:
            raise ValueError("RIVA_BASE_URL environment variable must be set")

        self.base_url = self.base_url.rstrip('/')
        logger.info(f"Setup client initialized with URL: {self.base_url}")

    def health_check(self) -> bool:
        """
        Simple health check for setup validation.
        Returns True if service is reachable, False otherwise.
        """
        try:
            # Try a simple GET request to the base URL
            response = requests.get(f"{self.base_url}/health", timeout=10)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            # Try alternative health check endpoints
            try:
                response = requests.get(f"{self.base_url}/v1/health", timeout=10)
                return response.status_code == 200
            except requests.exceptions.RequestException:
                try:
                    # Final fallback - just check if we can reach the base URL
                    response = requests.get(self.base_url, timeout=10)
                    return response.status_code in [200, 404, 405]  # Any response means it's reachable
                except requests.exceptions.RequestException as e:
                    logger.error(f"Health check failed: {e}")
                    return False
