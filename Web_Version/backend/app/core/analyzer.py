"""
Audio Analysis Core Module
Contains all audio analysis functions for ACX and ElevenLabs compliance checking
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, Tuple, Optional
import numpy as np
import librosa
import soundfile as sf
import pyloudnorm as pyln


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
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
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
        raise Exception(f"Error getting FFmpeg info: {e}")


def analyze_audio_levels(file_path: Path) -> Dict:
    """
    Analyze RMS, peak levels, and noise floor

    Args:
        file_path: Path to audio file

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

        for i in range(0, len(audio) - window_size, window_size):
            window_rms = np.sqrt(np.mean(audio[i:i+window_size]**2))
            windows.append(window_rms)

        windows.sort()
        noise_floor_rms = np.mean(windows[:max(1, len(windows)//10)])
        noise_floor_db = 20 * np.log10(noise_floor_rms + 1e-10)

        return {
            'rms_db': float(rms_db),
            'peak_db': float(peak_db),
            'noise_floor_db': float(noise_floor_db)
        }
    except Exception as e:
        raise Exception(f"Error analyzing audio levels: {e}")


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

        return (float(start_silence), float(end_silence))
    except Exception as e:
        raise Exception(f"Error detecting room tone: {e}")


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

        return (float(loudness), float(true_peak))
    except Exception as e:
        raise Exception(f"Error calculating LUFS: {e}")


def estimate_reverb_level(file_path: Path) -> str:
    """
    Estimate reverb/echo level in audio

    Returns:
        String describing reverb level (low, medium, high)
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
                return "low"
            elif decay_time < 0.5:
                return "medium"
            else:
                return "high"

        return "low"
    except Exception as e:
        return "unknown"


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
        'range': '-23 to -18 dB'
    }

    # Peak Level: < -3dB
    peak = analysis['peak_db']
    results['peak'] = {
        'value': peak,
        'pass': peak < -3,
        'threshold': '< -3 dB'
    }

    # Noise Floor: < -60dB
    noise = analysis['noise_floor_db']
    results['noise_floor'] = {
        'value': noise,
        'pass': noise < -60,
        'threshold': '< -60 dB'
    }

    # Format check
    format_pass = (
        analysis['sample_rate'] == 44100 and
        analysis['bitrate'] >= 192 and
        analysis['codec'] == 'mp3'
    )
    results['format'] = {
        'value': f"{analysis['codec'].upper()} ({analysis.get('format', 'unknown')}, {analysis['sample_rate']}Hz)",
        'pass': format_pass,
        'required': 'MP3 192+ kbps CBR, 44.1kHz'
    }

    # Duration check: < 120 minutes
    duration_seconds = analysis['duration']
    results['duration'] = {
        'value': duration_seconds,
        'pass': duration_seconds < 7200,  # 120 minutes in seconds
        'max': 7200
    }

    # Room tone check: 1-5 seconds at start/end
    start_silence, end_silence = analysis.get('room_tone', (0, 0))
    room_tone_pass = (1 <= start_silence <= 5) and (1 <= end_silence <= 5)
    results['room_tone'] = {
        'detected': room_tone_pass,
        'pass': room_tone_pass,
        'required': '1-5 seconds at start/end'
    }

    # Overall pass
    results['overall_pass'] = all(r['pass'] for r in results.values() if isinstance(r, dict) and 'pass' in r)

    return results


def check_elevenlabs_compliance(analysis: Dict) -> Dict:
    """
    Check if audio meets ElevenLabs guidelines

    Returns:
        Dictionary with pass/fail for voice cloning requirements
    """
    results = {}

    # Sufficient length (minimum ~1 minute, recommended 30+ minutes)
    duration_seconds = analysis['duration']
    duration_minutes = duration_seconds / 60
    length_pass = duration_minutes >= 1
    results['length_ok'] = length_pass
    results['length_minutes'] = float(duration_minutes)
    results['length_requirement'] = 'Minimum 1 minute (30+ recommended)'

    # Quality check (clean audio)
    noise_acceptable = analysis['noise_floor_db'] < -50
    results['quality_ok'] = noise_acceptable
    results['quality_requirement'] = 'Clean audio with minimal background noise'

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


def analyze_audio_file(file_path: Path, original_filename: str = None) -> Dict:
    """
    Perform complete analysis on a single audio file

    Args:
        file_path: Path to audio file
        original_filename: Original filename (optional, defaults to file_path.name)

    Returns:
        Complete analysis dictionary with all results
    """
    # Get basic info
    ffmpeg_info = get_ffmpeg_info(file_path)

    # Audio level analysis
    levels = analyze_audio_levels(file_path)

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
        'lufs': lufs,
        'true_peak': true_peak,
        'reverb_level': reverb
    }

    # Check compliance
    acx_results = check_acx_compliance(analysis)
    el_results = check_elevenlabs_compliance(analysis)

    # Format the final response
    return {
        'success': True,
        'file_info': {
            'filename': original_filename if original_filename else file_path.name,
            'duration': format_duration(analysis['duration']),
            'duration_seconds': analysis['duration'],
            'format': analysis['codec'].upper(),
            'sample_rate': analysis['sample_rate'],
            'channels': analysis['channels'],
            'bitrate': f"{analysis['bitrate']} kbps"
        },
        'acx_compliance': acx_results,
        'additional_metrics': {
            'lufs': analysis['lufs'],
            'true_peak': analysis['true_peak'],
            'reverb_level': analysis['reverb_level']
        },
        'elevenlabs': el_results
    }
