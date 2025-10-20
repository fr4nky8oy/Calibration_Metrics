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


def calculate_dynamic_range(file_path: Path) -> float:
    """
    Calculate dynamic range of audio (difference between loudest and quietest parts)

    Returns:
        Dynamic range in dB
    """
    try:
        audio, sr = librosa.load(str(file_path), sr=None, mono=True)

        # Calculate RMS in 1-second windows
        window_size = sr  # 1 second
        rms_values = []

        for i in range(0, len(audio) - window_size, window_size // 2):
            window = audio[i:i+window_size]
            rms = np.sqrt(np.mean(window**2))
            if rms > 1e-10:  # Ignore near-silence
                rms_values.append(20 * np.log10(rms))

        if len(rms_values) > 0:
            dynamic_range = max(rms_values) - min(rms_values)
            return float(dynamic_range)

        return 0.0
    except Exception as e:
        return 0.0


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
    Check if audio meets ElevenLabs guidelines for voice cloning

    Covers both Instant Voice Cloning and Professional Voice Cloning requirements
    Documentation links:
    - Instant: https://elevenlabs.io/docs/product-guides/voices/voice-cloning/instant-voice-cloning
    - Professional: https://elevenlabs.io/docs/product-guides/voices/voice-cloning/professional-voice-cloning

    Returns:
        Dictionary with detailed voice cloning suitability information
    """
    results = {}

    duration_seconds = analysis['duration']
    duration_minutes = duration_seconds / 60
    rms = analysis['rms_db']
    true_peak = analysis['true_peak']
    noise = analysis['noise_floor_db']
    reverb = analysis['reverb_level']
    dynamic_range = analysis.get('dynamic_range', 0)

    # 1. Volume/Loudness Requirements
    volume_ok = -23 <= rms <= -18 and true_peak <= -3
    results['volume'] = {
        'rms': rms,
        'true_peak': true_peak,
        'pass': volume_ok,
        'ideal_range': '-23 to -18 dB RMS, -3 dB true peak',
        'message': 'Volume is optimal for voice cloning' if volume_ok else 'Adjust volume to -23 to -18 dB RMS range'
    }

    # 2. Format Suitability
    codec = analysis['codec'].lower()
    bitrate = analysis['bitrate']
    format_ok = codec == 'mp3' and bitrate >= 192
    results['format'] = {
        'current': f"{analysis['codec'].upper()} at {bitrate} kbps",
        'pass': format_ok,
        'recommended': 'MP3 at 192+ kbps',
        'message': 'Format is suitable' if format_ok else 'Convert to MP3 192+ kbps for best results'
    }

    # 3. Audio Quality Checklist
    clean_audio = noise < -50
    low_reverb = reverb in ['low', 'unknown']
    consistent_volume = dynamic_range < 15  # Less than 15dB variation

    results['quality_checklist'] = {
        'clean_audio': {
            'pass': clean_audio,
            'value': f"{noise:.1f} dB",
            'message': 'Clean audio with low noise floor' if clean_audio else 'Background noise detected'
        },
        'no_reverb': {
            'pass': low_reverb,
            'value': reverb,
            'message': 'Minimal reverb/echo' if low_reverb else 'Reverb/echo detected - may affect clone quality'
        },
        'consistent_volume': {
            'pass': consistent_volume,
            'value': f"{dynamic_range:.1f} dB",
            'message': 'Consistent volume levels' if consistent_volume else 'High dynamic range - may yield unpredictable results'
        }
    }

    # 4. Duration-based cloning type recommendation
    if duration_minutes < 1:
        cloning_type = 'none'
        recommendation = 'Too short for voice cloning. Need minimum 1 minute.'
    elif duration_minutes <= 2:
        cloning_type = 'instant'
        recommendation = 'Ideal for Instant Voice Cloning (1-2 minutes is the sweet spot)'
    elif duration_minutes <= 3:
        cloning_type = 'instant'
        recommendation = 'Good for Instant Voice Cloning (longer may not improve quality)'
    elif duration_minutes < 30:
        cloning_type = 'neither'
        recommendation = 'Too long for Instant, too short for Professional. Use first 2 minutes for Instant or record more for Professional (30+ minutes recommended)'
    elif duration_minutes < 180:
        cloning_type = 'professional'
        recommendation = f'Suitable for Professional Voice Cloning ({duration_minutes:.1f} minutes)'
    else:
        cloning_type = 'professional'
        recommendation = f'Optimal for Professional Voice Cloning ({duration_minutes:.1f} minutes - excellent sample size)'

    results['cloning_type'] = {
        'recommended': cloning_type,
        'duration_minutes': float(duration_minutes),
        'message': recommendation
    }

    # 5. Overall Suitability Score
    criteria_met = 0
    total_criteria = 5

    if volume_ok:
        criteria_met += 1
    if format_ok:
        criteria_met += 1
    if clean_audio:
        criteria_met += 1
    if low_reverb:
        criteria_met += 1
    if consistent_volume:
        criteria_met += 1

    # Determine overall suitability
    if duration_minutes < 1:
        suitability = 'unsuitable'
        suitability_message = 'Not suitable for voice cloning - file too short'
    elif criteria_met >= 4:
        if cloning_type == 'instant':
            suitability = 'excellent'
            suitability_message = f'Excellent for Instant Voice Cloning ({criteria_met}/{total_criteria} criteria met)'
        elif cloning_type == 'professional':
            suitability = 'excellent'
            suitability_message = f'Excellent for Professional Voice Cloning ({criteria_met}/{total_criteria} criteria met)'
        else:
            suitability = 'good'
            suitability_message = f'Good audio quality ({criteria_met}/{total_criteria} criteria met) - adjust duration for optimal results'
    elif criteria_met >= 3:
        suitability = 'acceptable'
        suitability_message = f'Acceptable for voice cloning ({criteria_met}/{total_criteria} criteria met) - some improvements recommended'
    else:
        suitability = 'poor'
        suitability_message = f'Poor suitability ({criteria_met}/{total_criteria} criteria met) - significant improvements needed'

    results['overall'] = {
        'suitability': suitability,
        'criteria_met': criteria_met,
        'total_criteria': total_criteria,
        'message': suitability_message
    }

    # Documentation links
    results['documentation'] = {
        'instant_voice_cloning': 'https://elevenlabs.io/docs/product-guides/voices/voice-cloning/instant-voice-cloning',
        'professional_voice_cloning': 'https://elevenlabs.io/docs/product-guides/voices/voice-cloning/professional-voice-cloning'
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

    # Dynamic range calculation
    dynamic_range = calculate_dynamic_range(file_path)

    # Combine all analysis
    analysis = {
        **ffmpeg_info,
        **levels,
        'room_tone': room_tone,
        'lufs': lufs,
        'true_peak': true_peak,
        'reverb_level': reverb,
        'dynamic_range': dynamic_range
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
            'reverb_level': analysis['reverb_level'],
            'dynamic_range': analysis['dynamic_range']
        },
        'elevenlabs': el_results
    }
