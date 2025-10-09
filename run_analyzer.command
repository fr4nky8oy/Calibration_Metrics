#!/bin/bash

# Navigate to project directory
cd /Users/frankyredente/Music/Claude/CalibrationMetrics

# Activate virtual environment
source venv/bin/activate

# Run the audio analyzer with progress bar and text export
# Report will be saved with timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
python audio_analyzer.py --progress --output "analysis_report_${TIMESTAMP}.txt"

# Keep terminal open to see results
echo ""
echo "Press any key to close..."
read -n 1
