# Audio Analysis Tool for ACX & ElevenLabs Compliance

A professional command-line tool for analyzing audio files against [ACX audiobook standards](https://www.acx.com/help/acx-audio-submission-requirements/201456300) and [ElevenLabs voice cloning guidelines](https://elevenlabs.io/). Perfect for audiobook narrators, voice actors, and audio engineers who need to validate their recordings before submission.

## Features

✅ **ACX Audiobook Standards Validation**
- RMS level checking (-23 to -18 dB)
- Peak level analysis (< -3 dB)
- Noise floor measurement (< -60 dB)
- Format validation (192+ kbps CBR MP3, 44.1kHz)
- Duration limits (< 120 minutes)
- Room tone detection (1-5 seconds silence)

✅ **ElevenLabs Voice Cloning Guidelines**
- Minimum duration validation (1 minute minimum, 30+ minutes recommended)
- Audio quality assessment
- Background noise analysis

✅ **Additional Professional Metrics**
- LUFS (Loudness Units Full Scale) measurement
- True Peak detection
- Reverb/echo level estimation
- Batch processing with summary statistics

✅ **User Experience**
- Color-coded terminal output
- Progress bars for long audio files (>60 seconds)
- Detailed text report export
- Stream Deck integration (one-button operation)
- Batch folder analysis

## Installation

### Prerequisites
- Python 3.8 or higher
- FFmpeg (for format detection)

**Install FFmpeg:**
```bash
# macOS (using Homebrew)
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# Windows (using Chocolatey)
choco install ffmpeg
```

### Setup

1. Clone this repository:
```bash
git clone https://github.com/fr4nky8oy/CalibrationMetrics.git
cd CalibrationMetrics
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create audio files folder:
```bash
mkdir audio_files
```

## Usage

### Prepare Your Audio Files

**IMPORTANT:** This tool does not include sample audio files. You must provide your own audio files to analyze.

1. **Place your audio files** in the `audio_files/` folder (created during setup)
2. Supported formats: **MP3, WAV, FLAC, M4A**
3. You can analyze single files or entire folders

**Example folder structure:**
```
CalibrationMetrics/
├── audio_files/           # Put your audio files here!
│   ├── chapter1.mp3
│   ├── chapter2.mp3
│   └── narration_sample.wav
└── audio_analyzer.py
```

### Basic Analysis

Once you've added your audio files to the `audio_files/` folder, run:

```bash
python audio_analyzer.py
```

### Advanced Options

**Show progress bars for long files:**
```bash
python audio_analyzer.py --progress
```

**Export detailed text report:**
```bash
python audio_analyzer.py --output analysis_report.txt
```

**Analyze specific format only:**
```bash
python audio_analyzer.py --format mp3
```

**Analyze different folder:**
```bash
python audio_analyzer.py /path/to/audio/folder
```

**All features combined:**
```bash
python audio_analyzer.py --progress --output report.txt
```

### Stream Deck Integration (One-Button Operation)

Turn your audio analysis into a single button press with Elgato Stream Deck!

#### Step-by-Step Setup Guide

**1. Make the script executable** (one-time setup):
```bash
cd /Users/YOUR_USERNAME/path/to/CalibrationMetrics
chmod +x run_analyzer.command
```

**2. Configure Stream Deck:**

1. Open **Stream Deck** software on your computer
2. Find an empty button slot on your Stream Deck
3. From the actions list, drag **"System: Open"** to your chosen button
4. In the action settings:
   - Click **"Choose File..."**
   - Navigate to your project folder
   - Select **`run_analyzer.command`**
5. (Optional) Customize the button:
   - Add a title: "Audio Analysis" or "ACX Check"
   - Add an icon (microphone, audio wave, etc.)

**3. Usage:**
- Place audio files in the `audio_files/` folder
- Press your Stream Deck button
- Terminal opens automatically and runs the full analysis
- Results appear in terminal with color-coded pass/fail
- A timestamped report file is automatically created (e.g., `analysis_report_20251007_143022.txt`)

#### What the Stream Deck Button Does

The `run_analyzer.command` script automatically:
- Activates the Python virtual environment
- Runs the analyzer with `--progress` flag (shows progress bars for long files)
- Generates a timestamped text report with `--output` flag
- Shows all results in the terminal

#### Troubleshooting Stream Deck Setup

**Button doesn't work:**
- Ensure the script is executable: `chmod +x run_analyzer.command`
- Check the file path is correct in Stream Deck settings
- Verify Python virtual environment is set up: `ls venv/`

**Script runs but fails:**
- Make sure `audio_files/` folder exists and contains audio files
- Verify FFmpeg is installed: `ffmpeg -version`
- Check that all Python dependencies are installed: `pip list`

**Terminal closes immediately:**
- This is normal if no audio files are found
- Add audio files to `audio_files/` folder and try again

#### Alternative Automation Tools

This integration also works with:
- **Soundflow** - Audio production automation
- **Alfred** (macOS) - Productivity launcher
- **Keyboard Maestro** (macOS) - Macro automation
- **BetterTouchTool** - Custom gestures and shortcuts
- Any tool that can execute shell scripts

## Output Format

### Terminal Output
Color-coded results showing:
- ✅ **Green** = Pass
- ❌ **Red** = Fail
- File details (duration, format, bitrate, sample rate, channels)
- ACX compliance breakdown
- Additional metrics (LUFS, true peak, reverb)
- ElevenLabs compliance
- Summary statistics

### Text Report
Detailed report including:
- Complete file analysis for each audio file
- Pass/fail status for all requirements
- Specific measurements with tolerances
- Overall compliance summary
- Timestamped filename (when using Stream Deck)

## Libraries Used

### Core Audio Processing
- **[librosa](https://librosa.org/)** (0.10.1) - Audio analysis and feature extraction
- **[soundfile](https://python-soundfile.readthedocs.io/)** (0.12.1) - Audio file I/O operations
- **[numpy](https://numpy.org/)** (1.26.3) - Numerical computations and array operations

### Audio Measurement
- **[pyloudnorm](https://github.com/csteinmetz1/pyloudnorm)** (0.1.1) - LUFS loudness measurement (ITU-R BS.1770-4 standard)

### Format Detection
- **[FFmpeg](https://ffmpeg.org/)** - External tool for format and codec detection (via subprocess)

### User Interface
- **[tqdm](https://github.com/tqdm/tqdm)** (4.66.1) - Progress bars for long file analysis

### Python Standard Library
- `argparse` - Command-line argument parsing
- `json` - FFmpeg output parsing
- `pathlib` - Cross-platform file path handling
- `subprocess` - FFmpeg integration

## ACX Standards Reference

| Requirement | Standard | Tool Validates |
|------------|----------|----------------|
| RMS Level | -23 to -18 dB | ✅ |
| Peak Level | < -3 dB | ✅ |
| Noise Floor | < -60 dB RMS | ✅ |
| Format | 192+ kbps CBR MP3 | ✅ |
| Sample Rate | 44.1 kHz | ✅ |
| Room Tone | 1-5 seconds at start/end | ✅ |
| Max Duration | < 120 minutes | ✅ |

## ElevenLabs Guidelines Reference

| Requirement | Guideline | Tool Validates |
|------------|-----------|----------------|
| Minimum Length | 1 minute (30+ recommended) | ✅ |
| Audio Quality | Clean, minimal background noise | ✅ |
| Noise Floor | < -50 dB (recommended) | ✅ |

## Example Output

```
Scanning for audio files...
Found 3 audio file(s)

Analyzing: sample_narration.mp3... Done

============================================================
File: sample_narration.mp3
Duration: 2:34
Format: MP3, 192kbps, 44100Hz, Mono

ACX COMPLIANCE:
✓ RMS Level: -20.5 dB PASS: (-23 to -18 dB)
✓ Peak Level: -4.2 dB PASS: (< -3 dB)
✓ Noise Floor: -67.3 dB PASS: (< -60 dB)
✓ Format: PASS: (192+ kbps CBR MP3, 44.1kHz)
✓ Duration: 2.6 minutes PASS: (< 120 minutes)
✓ Room Tone: 2.1s start, 3.4s end PASS: (1-5 seconds)

ADDITIONAL METRICS:
LUFS: -21.3 LUFS
True Peak: -3.8 dBTP
Noise Level: -67.3 dB
Reverb Level: Low

ELEVENLABS COMPLIANCE:
✓ Length: 2.6 minutes (Minimum 1 minute (30+ recommended))
✓ Quality: Clean audio with minimal background noise

Overall: PASS (ACX Compliant)
------------------------------------------------------------

============================================================
SUMMARY STATISTICS
============================================================
Total files analyzed: 3
ACX Compliant: 2
Not Compliant: 1
Pass Rate: 66.7%
============================================================
```

## Troubleshooting

**Error: "FFmpeg not found"**
- Install FFmpeg using your package manager (see Installation section)

**Error: "No audio files found"**
- Check that audio files are in the `audio_files/` folder
- Supported formats: MP3, WAV, FLAC, M4A

**Files analyze slowly**
- This is normal - the tool performs thorough DSP analysis, not just metadata checking
- Use `--progress` flag to see real-time progress for files >60 seconds
- Typical speed: 30-60 seconds per minute of audio

**Virtual environment activation fails**
- Make sure you created it with `python3 -m venv venv`
- On Windows, use `venv\Scripts\activate` instead of `source venv/bin/activate`

## Common Audio Issues & Fixes

### RMS Too Quiet (< -23 dB)
**Solution:** Apply gain/normalization in your DAW to bring RMS into -23 to -18 dB range

### RMS Too Loud (> -18 dB)
**Solution:** Reduce gain or apply compression to lower overall level

### Missing Room Tone
**Solution:** Add 1-5 seconds of silence at beginning and end of file

### Wrong Format
**Solution:** Export as MP3 with these settings:
- Bitrate: 192 kbps (or higher)
- Mode: CBR (Constant Bitrate)
- Sample Rate: 44.1 kHz
- Channels: Mono or Stereo

### Noise Floor Too High
**Solution:**
- Record in quieter environment
- Use noise reduction tools (carefully - don't over-process)
- Check for electrical interference

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Author

**Franky Redente** - [GitHub](https://github.com/fr4nky8oy)

## Acknowledgments

- ACX for audiobook standards documentation
- ElevenLabs for voice cloning guidelines
- Audio engineering community for best practices

## Version History

**v1.0.0** (October 2025)
- Initial release
- ACX compliance checking
- ElevenLabs guidelines validation
- Progress bars for long files
- Text report export
- Stream Deck integration
- Batch processing with summary statistics

## Support

For issues, questions, or feature requests, please [open an issue](https://github.com/fr4nky8oy/CalibrationMetrics/issues).

---

**Note:** This tool validates against ACX technical standards and ElevenLabs guidelines. Always verify with official platform requirements before submission.
