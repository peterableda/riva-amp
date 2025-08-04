#!/bin/bash

# Install system dependencies for audio processing
apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    libsndfile1-dev \
    portaudio19-dev \
    python3-pyaudio

# Install Python dependencies
pip3 install -r requirements.txt
