# Audio Analysis Tool - Project Summary

## Project Overview
This is a command-line audio analysis tool that checks audio files against ACX audiobook standards and ElevenLabs voice cloning guidelines.

## What We Built
A complete Python-based batch audio analyzer that provides:
- ACX compliance checking (RMS, peak, noise floor, format, duration, room tone)
- ElevenLabs guidelines validation
- Additional metrics (LUFS, true peak, reverb estimation)
- Color-coded terminal output
- Batch processing with summary statistics
- **Progress bars for long files (>60 seconds)** ✨ NEW
- **Detailed text report export with timestamps** ✨ NEW
- **Stream Deck integration for one-button analysis** ✨ NEW

## Project Structure
```
CalibrationMetrics/
├── audio_analyzer.py        # Main analysis tool
├── requirements.txt         # Python dependencies (includes tqdm)
├── README.md               # Full documentation
├── CLAUDE.md               # This file - project summary for Claude
├── run_analyzer.command    # Stream Deck shell script
├── venv/                   # Virtual environment
├── audio_files/            # Default folder - add audio files here
└── analysis_report_*.txt   # Generated reports (timestamped)
```

## How to Use the Tool

### Stream Deck (EASIEST - One Button Press!)
1. Open Stream Deck software
2. Drag "System: Open" action to a button
3. Browse to `/Users/frankyredente/Music/Claude/CalibrationMetrics/run_analyzer.command`
4. Press the button to run analysis with progress bars and automatic timestamped report

### Command Line Usage

**Basic analysis:**
```bash
cd /Users/frankyredente/Music/Claude/CalibrationMetrics
source venv/bin/activate
python audio_analyzer.py
```

**With progress bars (for files >60 seconds):**
```bash
python audio_analyzer.py --progress
```

**With text report export:**
```bash
python audio_analyzer.py --output report.txt
```

**All features combined:**
```bash
python audio_analyzer.py --progress --output analysis_report.txt
```

**Other options:**
```bash
# Analyze specific format only
python audio_analyzer.py --format mp3

# Analyze different folder
python audio_analyzer.py /path/to/other/folder

# View all options
python audio_analyzer.py --help
```

### One-Line Command
```bash
cd /Users/frankyredente/Music/Claude/CalibrationMetrics && source venv/bin/activate && python audio_analyzer.py --progress --output report.txt
```

## Latest Analysis Results (Oct 7, 2025)

**Files Analyzed:** 5 WAV files (all short test recordings, 7-58 seconds)

**Results:** 0/5 passed ACX compliance (0% pass rate)

### Common Issues Found:
1. **Format** ❌ - All files are WAV (PCM_F32LE, 96kHz) instead of required MP3 (192+ kbps CBR, 44.1kHz)
2. **RMS Levels** ❌ - Most files too quiet (need -23 to -18 dB range)
   - File 03: -26.1 dB (close, needs +3-6 dB boost)
   - File 01: -72.7 dB (way too quiet, needs major boost)
   - File 02: -32.4 dB (needs +9-14 dB boost)
   - Vocal Booth: -26.2 dB (needs +3-8 dB boost)
   - File I_O: -67.3 dB (way too quiet, needs major boost)
3. **Room Tone** ❌ - Missing 1-5 seconds of silence at start/end
4. **Length** ❌ - All too short for ElevenLabs (under 1 minute, need 30+ minutes)

### What Passed:
- ✅ Noise floor excellent (all very clean, < -60 dB)
- ✅ Peak levels acceptable
- ✅ Audio quality good

### Recommendations to Fix:
1. Normalize/amplify audio to get RMS in -23 to -18 dB range
2. Add 1-5 seconds of room tone at beginning and end
3. Convert final files to MP3 (192+ kbps CBR, 44.1kHz sample rate)
4. For ElevenLabs voice cloning, need much longer recordings (30+ minutes recommended)

## Technical Stack
- **Language:** Python 3.13
- **Key Libraries:**
  - librosa - Audio analysis
  - soundfile - Audio I/O
  - pyloudnorm - LUFS measurements
  - numpy - Array operations
  - tqdm - Progress bars ✨ NEW
- **External Tool:** FFmpeg (for format detection)
- **Hardware Integration:** Elgato Stream Deck support ✨ NEW

## Installation (Already Complete)
```bash
# Virtual environment created
python3 -m venv venv

# Dependencies installed
source venv/bin/activate
pip install -r requirements.txt

# Stream Deck script made executable
chmod +x run_analyzer.command
```

## ACX Standards Reference (Quick)
- **RMS:** -23 to -18 dB
- **Peak:** < -3 dB
- **Noise Floor:** < -60 dB RMS
- **Format:** 192+ kbps CBR MP3, 44.1kHz
- **Room Tone:** 1-5 seconds at start/end
- **Max Duration:** 120 minutes per file

## Performance Notes
- Analysis time: ~30-60 seconds per minute of audio
- Short files (under 1 minute): ~20-90 seconds each
- The tool processes audio data thoroughly, not just metadata
- Progress bars show real-time analysis for files >60 seconds

## Report Output Format
Text reports include:
- File details (duration, format, bitrate, sample rate, channels)
- ACX compliance (RMS, peak, noise floor, format, duration, room tone)
- Additional metrics (LUFS, true peak, reverb level)
- ElevenLabs compliance (length, quality)
- Overall pass/fail status
- Summary statistics for batch analysis
- Timestamped filenames when using Stream Deck

## Stream Deck Integration
- **File:** `run_analyzer.command`
- **Features:** Automatically runs with `--progress` and `--output` flags
- **Output:** Creates timestamped report files (e.g., `analysis_report_20251007_143022.txt`)
- **Setup:** One-time configuration in Stream Deck software, then one-button operation
- **Also works with:** Soundflow or any automation tool that can execute shell scripts

## Future Improvements (If Needed)
- Add automatic audio normalization
- Add room tone injection feature
- Add batch MP3 conversion with correct settings
- Export results to CSV format
- Add custom threshold configurations

## Recent Updates
**October 7, 2025:**
- ✅ Added progress bars for long files (tqdm library)
- ✅ Added detailed text report export
- ✅ Created Stream Deck integration script
- ✅ Added `--progress` and `--output` command-line options
- ✅ Updated requirements.txt with tqdm dependency

## Last Updated
October 7, 2025
