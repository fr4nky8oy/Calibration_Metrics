# Audio Analysis Tool - Project Requirements

## Project Overview
Create a command-line batch audio analysis tool that checks audio files against ACX audiobook standards and ElevenLabs voice cloning guidelines.

## Objective
Build a terminal-based tool that analyzes multiple audio files in a folder and outputs detailed metrics for each file. No UI or application needed - purely command-line interface.

## Input
- Tool should scan a designated folder for audio files
- Support common audio formats: MP3, WAV, FLAC, M4A
- Process multiple files in batch

## Output Requirements
The tool must output the following metrics for each audio file:

### ACX Standard Checks
1. **RMS Level**: Must be between -23dB and -18dB
2. **Peak Level**: Must be less than -3dB
3. **Noise Floor**: Must be less than -60dB RMS
4. **Format Check**: 
   - Verify if file is 192 kbps or higher CBR MP3
   - Check if 44.1kHz sample rate
   - Verify mono or stereo (flag if mixed formats across files)
5. **Room Tone**: Detect silence at beginning/end (should be 1-5 seconds)
6. **File Duration**: Flag if longer than 120 minutes

### ElevenLabs Guidelines
Reference: https://elevenlabs.io/docs/product-guides/voices/voice-cloning/professional-voice-cloning#sufficient-audio-length

7. **Audio Length**: Check if sufficient length for voice cloning
8. **Quality Indicators**: 
   - Clean audio (minimal background noise)
   - Consistent voice samples

### Additional Metrics
9. **LUFS** (Loudness Units Full Scale): Measure integrated loudness
10. **True Peak**: Measure actual peak level
11. **Noise Level**: Measure background noise/hiss
12. **Reverb Level**: Detect and measure reverb/echo

## Technical Requirements

### Tools/Libraries to Use
- **FFmpeg**: For audio file analysis and format detection
- **ffmpeg-python** or subprocess calls to FFmpeg
- **pyloudnorm**: For LUFS measurements
- **librosa** or **pydub**: For audio analysis
- Python 3.x

### Functionality
1. **Scan folder**: Recursively find all audio files in specified directory
2. **Batch processing**: Analyze all files and generate report
3. **Pass/Fail indicators**: Clear flags for ACX compliance
4. **Detailed report**: Output results to terminal and optionally to text/CSV file
5. **Summary statistics**: Overall folder analysis summary

## Usage Pattern
```bash
# Basic usage - analyze all files in a folder
python audio_analyzer.py /path/to/audio/folder

# With output file
python audio_analyzer.py /path/to/audio/folder --output report.txt

# Specific format only
python audio_analyzer.py /path/to/audio/folder --format mp3
```

## Output Format Example
```
=== AUDIO ANALYSIS REPORT ===
File: audiobook_chapter1.mp3
Duration: 15:23
Format: MP3, 192kbps CBR, 44.1kHz, Stereo

ACX COMPLIANCE:
✓ RMS Level: -20.5 dB (PASS: -23 to -18 dB)
✓ Peak Level: -4.2 dB (PASS: < -3 dB)
✓ Noise Floor: -65.3 dB (PASS: < -60 dB)
✓ Format: Valid MP3 CBR
✗ Duration: 15 minutes (PASS: < 120 min)
✓ Room Tone: 2.1s start, 1.8s end

ADDITIONAL METRICS:
LUFS: -19.2 LUFS
True Peak: -2.8 dBTP
Noise Level: -68 dB
Reverb Level: Low (estimated)

ELEVENLABS COMPLIANCE:
✓ Sufficient length for voice cloning
✓ Audio quality acceptable

Overall: PASS (ACX Compliant)
---
```

## ACX Standards Reference

### Audio Quality Requirements
- **RMS**: -23dB to -18dB (consistent volume)
- **Peak**: Less than -3dB (avoid distortion)
- **Noise Floor**: Less than -60dB RMS
- **Room Tone**: 1-5 seconds at beginning/end
- **File Length**: Max 120 minutes per file
- **Format**: 192+ kbps CBR MP3, 44.1kHz
- **Channels**: All mono OR all stereo (consistent)

### Content Requirements
- Opening credits: Title, author, narrator
- Closing credits: "You have been listening to..." + title/author/narrator + "The End"
- Retail sample: 5 minutes or less
- Human narration required (no unauthorized AI/TTS)

### Audio Consistency
- Consistent audio levels across files
- No extra sounds (plosives, clicks, mouth noise)
- Consistent tone and spacing
- No background noise distractions

## Implementation Notes
- Use FFmpeg for format detection and basic analysis
- Use pyloudnorm for accurate LUFS measurements
- Implement noise floor detection using audio analysis
- Room tone detection: analyze first and last 10 seconds for silence
- Color-coded terminal output (green for pass, red for fail)
- Generate both human-readable and machine-readable reports

## Deliverables
1. Python script(s) for audio analysis
2. Requirements.txt for dependencies
3. README with installation and usage instructions
4. Example output/reports

## Project Location
`/Users/frankyredente/music/claude/CalibrationMetrics`