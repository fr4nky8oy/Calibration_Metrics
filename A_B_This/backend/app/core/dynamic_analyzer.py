"""
Dynamic range and compression analysis for A/B This
Analyzes RMS, peak levels, LUFS, and compression characteristics
"""

import numpy as np
import pyloudnorm as pyln
from typing import Dict


def analyze_dynamics(audio: np.ndarray, sr: int) -> Dict:
    """
    Analyze dynamic range and loudness characteristics

    Args:
        audio: Audio samples (mono or stereo)
        sr: Sample rate

    Returns:
        Dictionary with dynamic analysis results
    """
    # Ensure audio is 2D for stereo processing
    if audio.ndim == 1:
        audio = audio.reshape(1, -1)

    # Calculate RMS level
    rms = np.sqrt(np.mean(audio**2))
    rms_db = 20 * np.log10(rms + 1e-10)

    # Calculate peak level (true peak)
    peak = np.max(np.abs(audio))
    peak_db = 20 * np.log10(peak + 1e-10)

    # Calculate crest factor (peak to RMS ratio)
    crest_factor = peak_db - rms_db

    # Calculate LUFS (ITU-R BS.1770 standard)
    try:
        meter = pyln.Meter(sr)
        # Transpose audio for pyloudnorm (expects channels last)
        audio_for_lufs = audio.T if audio.ndim == 2 else audio

        lufs = meter.integrated_loudness(audio_for_lufs)
    except Exception:
        # Fallback if LUFS calculation fails
        lufs = rms_db + 3.0  # Rough approximation

    # Calculate PLR (Peak to Loudness Ratio) - dynamic range metric
    plr = peak_db - lufs

    return {
        'rms_db': round(float(rms_db), 1),
        'peak_db': round(float(peak_db), 1),
        'crest_factor': round(float(crest_factor), 1),
        'lufs_integrated': round(float(lufs), 1),
        'plr': round(float(plr), 1)
    }


def compare_dynamics(
    your_mix_dynamics: Dict,
    reference_dynamics: Dict
) -> Dict:
    """
    Compare dynamic characteristics between two tracks

    Args:
        your_mix_dynamics: Dynamics from analyze_dynamics()
        reference_dynamics: Dynamics from analyze_dynamics()

    Returns:
        Comparison results with suggestions
    """
    # Calculate differences
    rms_diff = your_mix_dynamics['rms_db'] - reference_dynamics['rms_db']
    lufs_diff = your_mix_dynamics['lufs_integrated'] - reference_dynamics['lufs_integrated']
    crest_diff = your_mix_dynamics['crest_factor'] - reference_dynamics['crest_factor']
    plr_diff = your_mix_dynamics['plr'] - reference_dynamics['plr']

    # Analyze compression characteristics
    compression_analysis = _analyze_compression_difference(crest_diff, plr_diff)

    # Analyze loudness
    loudness_analysis = _analyze_loudness_difference(lufs_diff, rms_diff)

    return {
        'differences': {
            'rms_db': round(rms_diff, 1),
            'lufs': round(lufs_diff, 1),
            'crest_factor': round(crest_diff, 1),
            'plr': round(plr_diff, 1)
        },
        'compression_comparison': compression_analysis,
        'loudness_comparison': loudness_analysis,
        'suggestions': _generate_dynamic_suggestions(
            lufs_diff,
            crest_diff,
            plr_diff,
            your_mix_dynamics,
            reference_dynamics
        )
    }


def _analyze_compression_difference(crest_diff: float, plr_diff: float) -> Dict:
    """
    Analyze compression characteristics based on crest factor and PLR

    Args:
        crest_diff: Your mix crest factor - reference crest factor
        plr_diff: Your mix PLR - reference PLR

    Returns:
        Compression analysis dictionary
    """
    # Positive crest_diff means your mix is MORE dynamic (less compressed)
    # Negative crest_diff means your mix is LESS dynamic (more compressed)

    if crest_diff > 3:
        status = "much_less_compressed"
        description = "Your mix is significantly less compressed than the reference"
    elif crest_diff > 1.5:
        status = "less_compressed"
        description = "Your mix is less compressed than the reference"
    elif crest_diff < -3:
        status = "much_more_compressed"
        description = "Your mix is significantly more compressed than the reference"
    elif crest_diff < -1.5:
        status = "more_compressed"
        description = "Your mix is more compressed than the reference"
    else:
        status = "similar"
        description = "Your mix has similar compression to the reference"

    return {
        'status': status,
        'description': description,
        'crest_factor_difference': round(crest_diff, 1),
        'dynamic_range_difference': round(plr_diff, 1)
    }


def _analyze_loudness_difference(lufs_diff: float, rms_diff: float) -> Dict:
    """
    Analyze loudness characteristics

    Args:
        lufs_diff: Your mix LUFS - reference LUFS
        rms_diff: Your mix RMS - reference RMS

    Returns:
        Loudness analysis dictionary
    """
    # Positive means your mix is louder
    # Negative means your mix is quieter

    if lufs_diff > 3:
        status = "much_louder"
    elif lufs_diff > 1:
        status = "louder"
    elif lufs_diff < -3:
        status = "much_quieter"
    elif lufs_diff < -1:
        status = "quieter"
    else:
        status = "similar"

    return {
        'status': status,
        'lufs_difference': round(lufs_diff, 1),
        'rms_difference': round(rms_diff, 1)
    }


def _generate_dynamic_suggestions(
    lufs_diff: float,
    crest_diff: float,
    plr_diff: float,
    your_mix: Dict,
    reference: Dict
) -> Dict:
    """
    Generate actionable suggestions for dynamics and compression

    Args:
        lufs_diff: LUFS difference
        crest_diff: Crest factor difference
        plr_diff: PLR difference
        your_mix: Your mix dynamics
        reference: Reference dynamics

    Returns:
        Dictionary with compression and loudness suggestions
    """
    suggestions = {
        'compression': None,
        'limiting': None,
        'gain': None
    }

    # Compression suggestions
    if crest_diff > 2:
        # Your mix is too dynamic
        compression_amount = round(crest_diff * 0.6, 1)
        method = 'parallel compression' if crest_diff > 4 else 'gentle compression'
        suggestions['compression'] = {
            'action': 'add_compression',
            'amount_db': compression_amount,
            'method': method,
            'message': f"Apply {compression_amount}dB of compression to match reference density. Consider {method} to maintain some dynamics."
        }
    elif crest_diff < -2:
        # Your mix is too compressed
        suggestions['compression'] = {
            'action': 'reduce_compression',
            'message': f"Your mix is {abs(round(crest_diff, 1))}dB more compressed than reference. Consider reducing compression or using less limiting to preserve dynamics."
        }

    # Loudness/gain suggestions
    if abs(lufs_diff) > 1.5:
        gain_adjustment = round(-lufs_diff, 1)
        suggestions['gain'] = {
            'action': 'adjust_gain',
            'amount_db': gain_adjustment,
            'message': f"{'Increase' if gain_adjustment > 0 else 'Decrease'} overall level by {abs(gain_adjustment)}dB to match reference loudness"
        }

    # Limiting suggestions (based on peak levels)
    peak_diff = your_mix['peak_db'] - reference['peak_db']
    if peak_diff > 1:
        suggestions['limiting'] = {
            'action': 'add_limiting',
            'message': f"Your peaks are {round(peak_diff, 1)}dB higher than reference. Consider using a limiter to control peaks."
        }

    return {k: v for k, v in suggestions.items() if v is not None}
