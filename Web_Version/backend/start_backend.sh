#!/bin/bash
# ACX Audio Analyzer - Local Backend Startup Script

echo "🎵 Starting ACX Audio Analyzer Backend..."
echo ""

# Activate virtual environment
source venv/bin/activate

# Start the server
echo "✅ Backend running at: http://localhost:8000"
echo "✅ Frontend URL: https://calibration-metrics.vercel.app"
echo ""
echo "📝 To use the app:"
echo "   1. Keep this terminal window open"
echo "   2. Open https://calibration-metrics.vercel.app in your browser"
echo "   3. Upload audio files and analyze!"
echo ""
echo "Press Ctrl+C to stop the backend"
echo ""

uvicorn app.main:app --host 0.0.0.0 --port 8000
