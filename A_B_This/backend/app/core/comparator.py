"""
Main comparison logic for A/B This
Orchestrates all analysis modules and combines results
"""

import librosa
import soundfile as sf
import numpy as np
from typing import Dict, Tuple, List
import time
from pathlib import Path

from .spectrum_analyzer import (
    analyze_frequency_balance,
    compare_frequency_balance,
    get_spectrum_data
)
from .masking_analyzer import analyze_frequency_masking, compare_masking
from .resonance_detector import detect_resonances, compare_resonances
from .dynamic_analyzer import analyze_dynamics, compare_dynamics
from .stereo_analyzer import analyze_stereo_width, compare_stereo_width


def compare_audio_files(
    your_mix_path: str,
    reference_path: str,
    downsample_sr: int = 22050,
    your_mix_region: Dict = None,
    reference_region: Dict = None
) -> Dict:
    """
    Complete audio comparison analysis

    Args:
        your_mix_path: Path to your mix file
        reference_path: Path to reference track file
        downsample_sr: Sample rate to downsample to for speed (default 22050)
        your_mix_region: Optional dict with 'start' and 'end' times in seconds
        reference_region: Optional dict with 'start' and 'end' times in seconds

    Returns:
        Comprehensive comparison results dictionary
    """
    start_time = time.time()

    # Load both files
    print(f"Loading files...")
    your_mix_audio, your_mix_info = _load_audio_file(your_mix_path, downsample_sr, your_mix_region)
    reference_audio, reference_info = _load_audio_file(reference_path, downsample_sr, reference_region)

    # Convert to mono for most analyses (except dynamics which needs stereo)
    your_mix_mono = librosa.to_mono(your_mix_audio)
    reference_mono = librosa.to_mono(reference_audio)

    print(f"Analyzing your mix...")
    # Analyze your mix
    your_mix_results = {
        'file_info': your_mix_info,
        'frequency_balance': analyze_frequency_balance(your_mix_mono, downsample_sr),
        'masking': analyze_frequency_masking(your_mix_mono, downsample_sr),
        'resonances': detect_resonances(your_mix_mono, downsample_sr),
        'dynamics': analyze_dynamics(your_mix_audio, downsample_sr),
        'stereo': analyze_stereo_width(your_mix_audio, downsample_sr),
        'spectrum_data': _get_spectrum_for_visualization(your_mix_mono, downsample_sr)
    }

    print(f"Analyzing reference...")
    # Analyze reference
    reference_results = {
        'file_info': reference_info,
        'frequency_balance': analyze_frequency_balance(reference_mono, downsample_sr),
        'masking': analyze_frequency_masking(reference_mono, downsample_sr),
        'resonances': detect_resonances(reference_mono, downsample_sr),
        'dynamics': analyze_dynamics(reference_audio, downsample_sr),
        'stereo': analyze_stereo_width(reference_audio, downsample_sr),
        'spectrum_data': _get_spectrum_for_visualization(reference_mono, downsample_sr)
    }

    print(f"Comparing results...")
    # Compare results
    comparison = {
        'frequency_balance': compare_frequency_balance(
            your_mix_results['frequency_balance'],
            reference_results['frequency_balance']
        ),
        'masking': compare_masking(
            your_mix_results['masking'],
            reference_results['masking']
        ),
        'resonances': compare_resonances(
            your_mix_results['resonances'],
            reference_results['resonances']
        ),
        'dynamics': compare_dynamics(
            your_mix_results['dynamics'],
            reference_results['dynamics']
        ),
        'stereo': compare_stereo_width(
            your_mix_results['stereo'],
            reference_results['stereo']
        )
    }

    # Compile all suggestions
    all_suggestions = _compile_suggestions(comparison)

    processing_time = time.time() - start_time

    return {
        'success': True,
        'processing_time': round(processing_time, 1),
        'your_mix': {
            'filename': Path(your_mix_path).name,
            'duration': your_mix_info['duration'],
            'format': your_mix_info['format'],
            'sample_rate': your_mix_info['sample_rate'],
            'channels': your_mix_info['channels'],
            'frequency_balance': your_mix_results['frequency_balance'],
            'masking': {
                'clarity_score': your_mix_results['masking']['clarity_score'],
                'issues': your_mix_results['masking']['masking_issues']
            },
            'resonances': your_mix_results['resonances'],
            'dynamics': your_mix_results['dynamics'],
            'stereo': your_mix_results['stereo'],
            'spectrum_data': your_mix_results['spectrum_data']
        },
        'reference': {
            'filename': Path(reference_path).name,
            'duration': reference_info['duration'],
            'format': reference_info['format'],
            'sample_rate': reference_info['sample_rate'],
            'channels': reference_info['channels'],
            'frequency_balance': reference_results['frequency_balance'],
            'masking': {
                'clarity_score': reference_results['masking']['clarity_score'],
                'issues': reference_results['masking']['masking_issues']
            },
            'resonances': reference_results['resonances'],
            'dynamics': reference_results['dynamics'],
            'stereo': reference_results['stereo'],
            'spectrum_data': reference_results['spectrum_data']
        },
        'comparison': comparison,
        'suggestions': all_suggestions
    }


def _load_audio_file(file_path: str, sr: int, region: Dict = None) -> Tuple[np.ndarray, Dict]:
    """
    Load audio file and extract metadata

    Args:
        file_path: Path to audio file
        sr: Target sample rate
        region: Optional dict with 'start' and 'end' times in seconds to trim audio

    Returns:
        Tuple of (audio_array, file_info_dict)
    """
    # Load audio
    audio, original_sr = librosa.load(file_path, sr=sr, mono=False)

    # Trim audio if region specified
    if region is not None:
        start_time = region.get('start', 0)
        end_time = region.get('end', None)

        start_sample = int(start_time * sr)
        end_sample = int(end_time * sr) if end_time is not None else None

        # Trim based on audio shape
        if audio.ndim == 1:
            # Mono audio
            audio = audio[start_sample:end_sample]
        else:
            # Stereo audio
            audio = audio[:, start_sample:end_sample]

    # Get file info
    try:
        info = sf.info(file_path)
        # Calculate duration from trimmed audio
        if audio.ndim == 1:
            duration = len(audio) / sr
        else:
            duration = audio.shape[1] / sr

        file_info = {
            'duration': round(duration, 1),
            'format': f"{info.format} {info.subtype}",
            'sample_rate': info.samplerate,
            'channels': info.channels,
            'bitrate': getattr(info, 'bitrate', 'N/A')
        }
    except Exception:
        # Fallback if soundfile can't read the format
        duration = len(audio.flatten()) / sr if audio.ndim == 1 else len(audio[0]) / sr
        channels = 1 if audio.ndim == 1 else audio.shape[0]
        file_info = {
            'duration': round(duration, 1),
            'format': Path(file_path).suffix.upper(),
            'sample_rate': sr,
            'channels': channels,
            'bitrate': 'N/A'
        }

    return audio, file_info


def _get_spectrum_for_visualization(audio: np.ndarray, sr: int, num_points: int = 200) -> Dict:
    """
    Get spectrum data optimized for visualization

    Args:
        audio: Mono audio samples
        sr: Sample rate
        num_points: Number of frequency points for graph (default 200)

    Returns:
        Dictionary with frequencies and magnitudes arrays
    """
    frequencies, magnitudes = get_spectrum_data(audio, sr)

    # Downsample to num_points for efficient frontend rendering
    if len(frequencies) > num_points:
        indices = np.linspace(0, len(frequencies) - 1, num_points, dtype=int)
        frequencies = frequencies[indices]
        magnitudes = magnitudes[indices]

    return {
        'frequencies': [round(float(f), 1) for f in frequencies],
        'magnitudes': [round(float(m), 1) for m in magnitudes]
    }


def _compile_suggestions(comparison: Dict) -> Dict:
    """
    Compile all suggestions from different analysis modules

    Args:
        comparison: Comparison results from all modules

    Returns:
        Dictionary with categorized suggestions
    """
    suggestions = {
        'eq_adjustments': [],
        'compression': None,
        'masking': [],
        'stereo': None,
        'summary': []
    }

    # EQ suggestions from frequency balance
    if comparison['frequency_balance']['problem_bands']:
        for problem in comparison['frequency_balance']['problem_bands']:
            suggestions['eq_adjustments'].append(problem['suggestion'])

    # EQ suggestions from resonances
    if comparison['resonances']['problem_resonances']:
        for problem in comparison['resonances']['problem_resonances']:
            suggestions['eq_adjustments'].append(problem['suggestion'])

    # Compression suggestions from dynamics
    dynamic_suggestions = comparison['dynamics'].get('suggestions', {})
    if dynamic_suggestions:
        suggestions['compression'] = dynamic_suggestions.get('compression')
        if dynamic_suggestions.get('crest_factor'):
            suggestions['crest_factor'] = dynamic_suggestions['crest_factor']
        if dynamic_suggestions.get('gain'):
            suggestions['gain'] = dynamic_suggestions['gain']
        if dynamic_suggestions.get('limiting'):
            suggestions['limiting'] = dynamic_suggestions['limiting']

    # Masking suggestions
    if comparison['masking']['suggestions']:
        suggestions['masking'] = comparison['masking']['suggestions']

    # Stereo suggestions
    stereo_comp = comparison.get('stereo', {})
    if not stereo_comp.get('both_mono') and stereo_comp.get('suggestions'):
        suggestions['stereo'] = stereo_comp['suggestions']

    # Generate summary
    suggestions['summary'] = _generate_summary(comparison)

    return suggestions


def _generate_summary(comparison: Dict) -> List[str]:
    """Generate high-level summary of main issues and recommendations"""

    summary = []

    # Frequency balance issues
    problem_bands = comparison['frequency_balance']['problem_bands']
    if problem_bands:
        high_severity = [p for p in problem_bands if p['severity'] == 'high']
        if high_severity:
            bands_str = ', '.join([p['band'].replace('_', ' ') for p in high_severity])
            summary.append(f"Major frequency imbalance in: {bands_str}")

    # Masking issues
    masking_comp = comparison['masking']
    clarity_diff = masking_comp['clarity_difference']
    if clarity_diff < -15:
        summary.append(f"Significant frequency masking detected (clarity score: {masking_comp['your_mix_clarity']}/100)")

    # Resonance issues
    resonance_comp = comparison['resonances']
    if resonance_comp['your_high_severity'] > resonance_comp['reference_high_severity'] + 1:
        summary.append(f"Multiple harsh resonances detected ({resonance_comp['your_high_severity']} severe peaks)")

    # Dynamics issues
    dynamics_comp = comparison['dynamics']
    compression_status = dynamics_comp['compression_comparison']['status']
    if compression_status in ['much_less_compressed', 'much_more_compressed']:
        summary.append(dynamics_comp['compression_comparison']['description'])

    # If no major issues
    if not summary:
        summary.append("Your mix is well-balanced overall! Minor tweaks suggested below.")

    return summary
