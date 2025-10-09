#!/usr/bin/env python3
"""
Audio Analysis Tool for ACX and ElevenLabs Compliance
Analyzes audio files against ACX audiobook standards and ElevenLabs voice cloning guidelines
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import numpy as np
import librosa
import soundfile as sf
import pyloudnorm as pyln
from tqdm import tqdm

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_colored(text: str, color: str) -> None:
    """Print text with color"""
    print(f"{color}{text}{Colors.END}")

def find_audio_files(directory: str, format_filter: Optional[str] = None) -> List[Path]:
    """
    Recursively find all audio files in the specified directory

    Args:
        directory: Path to search
        format_filter: Optional format filter (mp3, wav, flac, m4a)

    Returns:
        List of Path objects for audio files
    """
    supported_formats = ['.mp3', '.wav', '.flac', '.m4a']
    if format_filter:
        supported_formats = [f'.{format_filter.lower()}']

    audio_files = []
    path = Path(directory)

    if not path.exists():
        print_colored(f"Error: Directory '{directory}' does not exist", Colors.RED)
        return []

    for file_path in path.rglob('*'):
        if file_path.is_file() and file_path.suffix.lower() in supported_formats:
            audio_files.append(file_path)

    return sorted(audio_files)

def get_ffmpeg_info(file_path: Path) -> Dict:
    """
    Get audio file information using FFmpeg

    Returns:
        Dictionary with format, sample_rate, channels, bitrate, duration
    """
    try:
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json',
            '-show_format', '-show_streams', str(file_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        data = json.loads(result.stdout)

        audio_stream = None
        for stream in data.get('streams', []):
            if stream.get('codec_type') == 'audio':
                audio_stream = stream
                break

        if not audio_stream:
            return {}

        format_info = data.get('format', {})

        return {
            'codec': audio_stream.get('codec_name', 'unknown'),
            'sample_rate': int(audio_stream.get('sample_rate', 0)),
            'channels': int(audio_stream.get('channels', 0)),
            'bitrate': int(format_info.get('bit_rate', 0)) // 1000,  # Convert to kbps
            'duration': float(format_info.get('duration', 0)),
            'format': format_info.get('format_name', 'unknown')
        }
    except Exception as e:
        print_colored(f"Error getting FFmpeg info: {e}", Colors.RED)
        return {}

def analyze_audio_levels(file_path: Path, show_progress: bool = False) -> Dict:
    """
    Analyze RMS, peak levels, and noise floor

    Args:
        file_path: Path to audio file
        show_progress: Whether to show progress bar for long files

    Returns:
        Dictionary with rms_db, peak_db, noise_floor_db
    """
    try:
        # Load audio file
        audio, sr = librosa.load(str(file_path), sr=None, mono=False)

        # Convert to mono if stereo for consistent analysis
        if audio.ndim > 1:
            audio = np.mean(audio, axis=0)

        # Calculate RMS level
        rms = np.sqrt(np.mean(audio**2))
        rms_db = 20 * np.log10(rms + 1e-10)

        # Calculate peak level
        peak = np.max(np.abs(audio))
        peak_db = 20 * np.log10(peak + 1e-10)

        # Estimate noise floor (bottom 10% of RMS values in small windows)
        window_size = int(0.1 * sr)  # 100ms windows
        windows = []

        # Calculate number of windows
        num_windows = (len(audio) - window_size) // window_size

        # Show progress bar only for files with duration > 60 seconds
        duration = len(audio) / sr
        use_progress = show_progress and duration > 60

        iterator = range(0, len(audio) - window_size, window_size)
        if use_progress:
            iterator = tqdm(iterator, desc="  Analyzing windows", total=num_windows, leave=False)

        for i in iterator:
            window_rms = np.sqrt(np.mean(audio[i:i+window_size]**2))
            windows.append(window_rms)

        windows.sort()
        noise_floor_rms = np.mean(windows[:max(1, len(windows)//10)])
        noise_floor_db = 20 * np.log10(noise_floor_rms + 1e-10)

        return {
            'rms_db': rms_db,
            'peak_db': peak_db,
            'noise_floor_db': noise_floor_db
        }
    except Exception as e:
        print_colored(f"Error analyzing audio levels: {e}", Colors.RED)
        return {
            'rms_db': 0,
            'peak_db': 0,
            'noise_floor_db': 0
        }

def detect_room_tone(file_path: Path, sr: int = 44100) -> Tuple[float, float]:
    """
    Detect silence duration at beginning and end of audio

    Returns:
        Tuple of (start_silence_seconds, end_silence_seconds)
    """
    try:
        audio, sr = librosa.load(str(file_path), sr=sr, mono=True)

        # Threshold for silence detection (-40dB)
        threshold = 10**(-40/20)

        # Detect start silence
        start_silence = 0
        for i in range(len(audio)):
            if abs(audio[i]) > threshold:
                start_silence = i / sr
                break

        # Detect end silence
        end_silence = 0
        for i in range(len(audio) - 1, -1, -1):
            if abs(audio[i]) > threshold:
                end_silence = (len(audio) - 1 - i) / sr
                break

        return (start_silence, end_silence)
    except Exception as e:
        print_colored(f"Error detecting room tone: {e}", Colors.RED)
        return (0, 0)

def calculate_lufs(file_path: Path) -> Tuple[float, float]:
    """
    Calculate LUFS (Loudness Units Full Scale) and True Peak

    Returns:
        Tuple of (lufs, true_peak_db)
    """
    try:
        # Load audio
        data, rate = sf.read(str(file_path))

        # If stereo, convert to proper format
        if data.ndim == 1:
            data = data.reshape(-1, 1)

        # Create loudness meter
        meter = pyln.Meter(rate)

        # Measure loudness
        loudness = meter.integrated_loudness(data)

        # Calculate true peak
        true_peak = 20 * np.log10(np.max(np.abs(data)) + 1e-10)

        return (loudness, true_peak)
    except Exception as e:
        print_colored(f"Error calculating LUFS: {e}", Colors.RED)
        return (0, 0)

def estimate_reverb_level(file_path: Path) -> str:
    """
    Estimate reverb/echo level in audio

    Returns:
        String describing reverb level (Low, Medium, High)
    """
    try:
        audio, sr = librosa.load(str(file_path), sr=None, mono=True, duration=30)

        # Analyze decay time using autocorrelation
        autocorr = np.correlate(audio, audio, mode='full')
        autocorr = autocorr[len(autocorr)//2:]

        # Normalize
        autocorr = autocorr / autocorr[0]

        # Find decay rate
        decay_threshold = 0.1
        decay_samples = np.where(autocorr < decay_threshold)[0]

        if len(decay_samples) > 0:
            decay_time = decay_samples[0] / sr
            if decay_time < 0.2:
                return "Low"
            elif decay_time < 0.5:
                return "Medium"
            else:
                return "High"

        return "Low"
    except Exception as e:
        return "Unknown"

def check_acx_compliance(analysis: Dict) -> Dict:
    """
    Check if audio meets ACX standards

    Returns:
        Dictionary with pass/fail for each requirement
    """
    results = {}

    # RMS Level: -23dB to -18dB
    rms = analysis['rms_db']
    results['rms'] = {
        'value': rms,
        'pass': -23 <= rms <= -18,
        'requirement': '-23 to -18 dB'
    }

    # Peak Level: < -3dB
    peak = analysis['peak_db']
    results['peak'] = {
        'value': peak,
        'pass': peak < -3,
        'requirement': '< -3 dB'
    }

    # Noise Floor: < -60dB
    noise = analysis['noise_floor_db']
    results['noise_floor'] = {
        'value': noise,
        'pass': noise < -60,
        'requirement': '< -60 dB'
    }

    # Format check
    format_pass = (
        analysis['sample_rate'] == 44100 and
        analysis['bitrate'] >= 192 and
        analysis['codec'] == 'mp3'
    )
    results['format'] = {
        'pass': format_pass,
        'requirement': '192+ kbps CBR MP3, 44.1kHz'
    }

    # Duration check: < 120 minutes
    duration_minutes = analysis['duration'] / 60
    results['duration'] = {
        'value': duration_minutes,
        'pass': duration_minutes < 120,
        'requirement': '< 120 minutes'
    }

    # Room tone check: 1-5 seconds at start/end
    start_silence, end_silence = analysis.get('room_tone', (0, 0))
    room_tone_pass = (1 <= start_silence <= 5) and (1 <= end_silence <= 5)
    results['room_tone'] = {
        'start': start_silence,
        'end': end_silence,
        'pass': room_tone_pass,
        'requirement': '1-5 seconds'
    }

    return results

def check_elevenlabs_compliance(analysis: Dict) -> Dict:
    """
    Check if audio meets ElevenLabs guidelines

    Returns:
        Dictionary with pass/fail for voice cloning requirements
    """
    results = {}

    # Sufficient length (minimum ~1 minute, recommended 30+ minutes)
    duration_minutes = analysis['duration'] / 60
    length_pass = duration_minutes >= 1
    results['length'] = {
        'value': duration_minutes,
        'pass': length_pass,
        'requirement': 'Minimum 1 minute (30+ recommended)'
    }

    # Quality check (clean audio)
    noise_acceptable = analysis['noise_floor_db'] < -50
    results['quality'] = {
        'pass': noise_acceptable,
        'requirement': 'Clean audio with minimal background noise'
    }

    return results

def format_duration(seconds: float) -> str:
    """Format duration as MM:SS or HH:MM:SS"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes}:{secs:02d}"

def print_file_analysis(file_path: Path, analysis: Dict, acx_results: Dict, el_results: Dict) -> bool:
    """
    Print detailed analysis for a single file

    Returns:
        True if ACX compliant, False otherwise
    """
    print_colored(f"\n{'='*60}", Colors.BLUE)
    print_colored(f"File: {file_path.name}", Colors.BOLD)
    print(f"Duration: {format_duration(analysis['duration'])}")

    channels_str = "Mono" if analysis['channels'] == 1 else f"Stereo ({analysis['channels']} channels)"
    print(f"Format: {analysis['codec'].upper()}, {analysis['bitrate']}kbps, {analysis['sample_rate']}Hz, {channels_str}")

    # ACX Compliance
    print_colored("\nACX COMPLIANCE:", Colors.BOLD)

    def print_check(name: str, result: Dict, unit: str = ""):
        symbol = "✓" if result['pass'] else "✗"
        color = Colors.GREEN if result['pass'] else Colors.RED
        value_str = f"{result['value']:.1f}{unit}" if 'value' in result else ""
        req_str = f"({result['requirement']})" if value_str else result['requirement']
        status = "PASS" if result['pass'] else "FAIL"
        print_colored(f"{symbol} {name}: {value_str} {status}: {req_str}", color)

    print_check("RMS Level", acx_results['rms'], " dB")
    print_check("Peak Level", acx_results['peak'], " dB")
    print_check("Noise Floor", acx_results['noise_floor'], " dB")
    print_check("Format", acx_results['format'])
    print_check("Duration", acx_results['duration'], " minutes")

    rt = acx_results['room_tone']
    symbol = "✓" if rt['pass'] else "✗"
    color = Colors.GREEN if rt['pass'] else Colors.RED
    print_colored(f"{symbol} Room Tone: {rt['start']:.1f}s start, {rt['end']:.1f}s end (PASS: {rt['requirement']})", color)

    # Additional Metrics
    print_colored("\nADDITIONAL METRICS:", Colors.BOLD)
    lufs, true_peak = analysis.get('lufs', (0, 0))
    print(f"LUFS: {lufs:.1f} LUFS")
    print(f"True Peak: {true_peak:.1f} dBTP")
    print(f"Noise Level: {analysis['noise_floor_db']:.1f} dB")
    print(f"Reverb Level: {analysis.get('reverb_level', 'Unknown')}")

    # ElevenLabs Compliance
    print_colored("\nELEVENLABS COMPLIANCE:", Colors.BOLD)

    el_length = el_results['length']
    symbol = "✓" if el_length['pass'] else "✗"
    color = Colors.GREEN if el_length['pass'] else Colors.RED
    print_colored(f"{symbol} Length: {el_length['value']:.1f} minutes ({el_length['requirement']})", color)

    el_quality = el_results['quality']
    symbol = "✓" if el_quality['pass'] else "✗"
    color = Colors.GREEN if el_quality['pass'] else Colors.RED
    print_colored(f"{symbol} Quality: {el_quality['requirement']}", color)

    # Overall result
    acx_pass = all(r['pass'] for r in acx_results.values())
    overall = "PASS (ACX Compliant)" if acx_pass else "FAIL (Not ACX Compliant)"
    color = Colors.GREEN if acx_pass else Colors.RED
    print_colored(f"\nOverall: {overall}", color)
    print_colored("-" * 60, Colors.BLUE)

    return acx_pass

def analyze_file(file_path: Path, show_progress: bool = False) -> Tuple[Dict, Dict, Dict]:
    """
    Perform complete analysis on a single audio file

    Args:
        file_path: Path to audio file
        show_progress: Whether to show progress bar for long files

    Returns:
        Tuple of (analysis_dict, acx_results, elevenlabs_results)
    """
    print(f"Analyzing: {file_path.name}...", end=' ')
    sys.stdout.flush()

    # Get basic info
    ffmpeg_info = get_ffmpeg_info(file_path)

    # Determine if file is long (> 60 seconds)
    duration = ffmpeg_info.get('duration', 0)
    is_long_file = duration > 60

    if is_long_file and show_progress:
        print()  # New line for progress bars

    # Audio level analysis
    levels = analyze_audio_levels(file_path, show_progress=show_progress)

    # Room tone detection
    room_tone = detect_room_tone(file_path)

    # LUFS calculation
    lufs, true_peak = calculate_lufs(file_path)

    # Reverb estimation
    reverb = estimate_reverb_level(file_path)

    # Combine all analysis
    analysis = {
        **ffmpeg_info,
        **levels,
        'room_tone': room_tone,
        'lufs': (lufs, true_peak),
        'reverb_level': reverb
    }

    # Check compliance
    acx_results = check_acx_compliance(analysis)
    el_results = check_elevenlabs_compliance(analysis)

    if not (is_long_file and show_progress):
        print("Done")

    return (analysis, acx_results, el_results)

def generate_summary(results: List[Tuple[Path, bool]]) -> None:
    """Generate summary statistics for all analyzed files"""
    print_colored(f"\n{'='*60}", Colors.BLUE)
    print_colored("SUMMARY STATISTICS", Colors.BOLD)
    print_colored("="*60, Colors.BLUE)

    total = len(results)
    passed = sum(1 for _, acx_pass in results if acx_pass)
    failed = total - passed

    print(f"Total files analyzed: {total}")
    print_colored(f"ACX Compliant: {passed}", Colors.GREEN)
    print_colored(f"Not Compliant: {failed}", Colors.RED)

    if total > 0:
        pass_rate = (passed / total) * 100
        print(f"Pass Rate: {pass_rate:.1f}%")

    print_colored("="*60, Colors.BLUE)

def save_report(output_file: str, results_data: List) -> None:
    """Save analysis results to a text file"""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("AUDIO ANALYSIS REPORT\n")
            f.write("=" * 80 + "\n")
            f.write(f"Generated: {format_duration(0)}\n")  # Could add timestamp here
            f.write("=" * 80 + "\n\n")

            for data in results_data:
                file_path, analysis, acx_results, el_results = data
                acx_pass = all(r['pass'] for r in acx_results.values())

                f.write("=" * 80 + "\n")
                f.write(f"File: {file_path.name}\n")
                f.write("-" * 80 + "\n")
                f.write(f"Duration: {format_duration(analysis['duration'])}\n")

                channels_str = "Mono" if analysis['channels'] == 1 else f"Stereo ({analysis['channels']} channels)"
                f.write(f"Format: {analysis['codec'].upper()}, {analysis['bitrate']}kbps, ")
                f.write(f"{analysis['sample_rate']}Hz, {channels_str}\n\n")

                # ACX Compliance Section
                f.write("ACX COMPLIANCE:\n")
                f.write("-" * 40 + "\n")

                # RMS Level
                rms = acx_results['rms']
                status = "PASS" if rms['pass'] else "FAIL"
                f.write(f"  RMS Level: {rms['value']:.1f} dB [{status}] (Req: {rms['requirement']})\n")

                # Peak Level
                peak = acx_results['peak']
                status = "PASS" if peak['pass'] else "FAIL"
                f.write(f"  Peak Level: {peak['value']:.1f} dB [{status}] (Req: {peak['requirement']})\n")

                # Noise Floor
                noise = acx_results['noise_floor']
                status = "PASS" if noise['pass'] else "FAIL"
                f.write(f"  Noise Floor: {noise['value']:.1f} dB [{status}] (Req: {noise['requirement']})\n")

                # Format
                fmt = acx_results['format']
                status = "PASS" if fmt['pass'] else "FAIL"
                f.write(f"  Format: [{status}] (Req: {fmt['requirement']})\n")

                # Duration
                dur = acx_results['duration']
                status = "PASS" if dur['pass'] else "FAIL"
                f.write(f"  Duration: {dur['value']:.1f} minutes [{status}] (Req: {dur['requirement']})\n")

                # Room Tone
                rt = acx_results['room_tone']
                status = "PASS" if rt['pass'] else "FAIL"
                f.write(f"  Room Tone: {rt['start']:.1f}s start, {rt['end']:.1f}s end [{status}] (Req: {rt['requirement']})\n")

                # Overall ACX Result
                overall = "PASS (ACX Compliant)" if acx_pass else "FAIL (Not ACX Compliant)"
                f.write(f"\n  Overall: {overall}\n\n")

                # Additional Metrics Section
                f.write("ADDITIONAL METRICS:\n")
                f.write("-" * 40 + "\n")
                lufs, true_peak = analysis.get('lufs', (0, 0))
                f.write(f"  LUFS: {lufs:.1f} LUFS\n")
                f.write(f"  True Peak: {true_peak:.1f} dBTP\n")
                f.write(f"  Noise Level: {analysis['noise_floor_db']:.1f} dB\n")
                f.write(f"  Reverb Level: {analysis.get('reverb_level', 'Unknown')}\n\n")

                # ElevenLabs Compliance Section
                f.write("ELEVENLABS COMPLIANCE:\n")
                f.write("-" * 40 + "\n")

                el_length = el_results['length']
                status = "PASS" if el_length['pass'] else "FAIL"
                f.write(f"  Length: {el_length['value']:.1f} minutes [{status}] ({el_length['requirement']})\n")

                el_quality = el_results['quality']
                status = "PASS" if el_quality['pass'] else "FAIL"
                f.write(f"  Quality: [{status}] ({el_quality['requirement']})\n")

                f.write("\n" + "=" * 80 + "\n\n")

            # Summary Section
            total = len(results_data)
            passed = sum(1 for _, analysis, acx_results, _ in results_data
                        if all(r['pass'] for r in acx_results.values()))
            failed = total - passed
            pass_rate = (passed / total * 100) if total > 0 else 0

            f.write("\n" + "=" * 80 + "\n")
            f.write("SUMMARY STATISTICS\n")
            f.write("=" * 80 + "\n")
            f.write(f"Total files analyzed: {total}\n")
            f.write(f"ACX Compliant: {passed}\n")
            f.write(f"Not Compliant: {failed}\n")
            f.write(f"Pass Rate: {pass_rate:.1f}%\n")
            f.write("=" * 80 + "\n")

        print_colored(f"\nReport saved to: {output_file}", Colors.GREEN)
    except Exception as e:
        print_colored(f"Error saving report: {e}", Colors.RED)

def main():
    parser = argparse.ArgumentParser(
        description='Audio Analysis Tool for ACX and ElevenLabs Compliance'
    )
    parser.add_argument('directory', nargs='?', default='audio_files',
                        help='Directory containing audio files to analyze (default: audio_files)')
    parser.add_argument('--output', '-o', help='Output text file for detailed report (optional)')
    parser.add_argument('--format', '-f', help='Filter by format (mp3, wav, flac, m4a)')
    parser.add_argument('--progress', '-p', action='store_true',
                        help='Show progress bars for long files (> 60 seconds)')

    args = parser.parse_args()

    # Find audio files
    print_colored("Scanning for audio files...", Colors.BLUE)
    audio_files = find_audio_files(args.directory, args.format)

    if not audio_files:
        print_colored("No audio files found.", Colors.RED)
        return

    print(f"Found {len(audio_files)} audio file(s)\n")

    # Analyze each file
    results = []
    results_data = []

    for file_path in audio_files:
        try:
            analysis, acx_results, el_results = analyze_file(file_path, show_progress=args.progress)
            acx_pass = print_file_analysis(file_path, analysis, acx_results, el_results)
            results.append((file_path, acx_pass))
            results_data.append((file_path, analysis, acx_results, el_results))
        except Exception as e:
            print_colored(f"Error analyzing {file_path.name}: {e}", Colors.RED)
            results.append((file_path, False))

    # Generate summary
    generate_summary(results)

    # Save report if requested
    if args.output:
        save_report(args.output, results_data)

if __name__ == '__main__':
    main()
