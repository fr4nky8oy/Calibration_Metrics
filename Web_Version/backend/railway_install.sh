#!/bin/bash
# Railway install script - installs system dependencies

echo "Installing ffmpeg..."
apt-get update
apt-get install -y ffmpeg
echo "FFmpeg installed successfully"

# Verify installation
which ffprobe
ffprobe -version
