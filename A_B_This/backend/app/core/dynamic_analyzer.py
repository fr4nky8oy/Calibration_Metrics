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
    compression_analysis = _analyze_compression_difference(
        crest_diff,
        plr_diff,
        your_mix_dynamics['crest_factor'],
        reference_dynamics['crest_factor']
    )

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


def _analyze_compression_difference(
    crest_diff: float,
    plr_diff: float,
    your_crest: float,
    reference_crest: float
) -> Dict:
    """
    Analyze compression characteristics based on crest factor and PLR

    Args:
        crest_diff: Your mix crest factor - reference crest factor
        plr_diff: Your mix PLR - reference PLR
        your_crest: Your mix crest factor
        reference_crest: Reference crest factor

    Returns:
        Compression analysis dictionary
    """
    # Positive crest_diff means your mix is MORE dynamic (less compressed)
    # Negative crest_diff means your mix is LESS dynamic (more compressed)

    if crest_diff > 3:
        status = "much_less_compressed"
        description = "Your mix is significantly less compressed than the reference"
    elif crest_diff > 1.0:
        status = "less_compressed"
        description = "Your mix is less compressed than the reference"
    elif crest_diff < -3:
        status = "much_more_compressed"
        description = "Your mix is significantly more compressed than the reference"
    elif crest_diff < -1.0:
        status = "more_compressed"
        description = "Your mix is more compressed than the reference"
    else:
        status = "well_matched"
        description = "Your mix has well-matched compression to the reference"

    return {
        'status': status,
        'description': description,
        'crest_factor_difference': round(crest_diff, 1),
        'dynamic_range_difference': round(plr_diff, 1),
        'your_crest_factor': round(your_crest, 1),
        'reference_crest_factor': round(reference_crest, 1)
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
        description = "Your mix is significantly louder than the reference"
    elif lufs_diff > 1:
        status = "louder"
        description = "Your mix is louder than the reference"
    elif lufs_diff < -3:
        status = "much_quieter"
        description = "Your mix is significantly quieter than the reference"
    elif lufs_diff < -1:
        status = "quieter"
        description = "Your mix is quieter than the reference"
    else:
        status = "well_matched"
        description = "Your mix has well-matched loudness to the reference"

    return {
        'status': status,
        'description': description,
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
        'gain': None,
        'crest_factor': None
    }

    # Crest Factor / Compression suggestions
    if crest_diff > 3:
        # Your mix is significantly too dynamic
        compression_amount = round(crest_diff * 0.6, 1)
        suggestions['crest_factor'] = {
            'action': 'add_compression',
            'amount_db': compression_amount,
            'difference': round(crest_diff, 1),
            'message': f"Your mix is {round(crest_diff, 1)}dB more dynamic than reference. Add {compression_amount}dB of parallel compression on the mix bus. Try a ratio of 4:1 with slow attack (30-50ms) and medium release (auto or 100-200ms). This will reduce the crest factor while maintaining transient punch.",
            'recommended_plugins': "iZotope Ozone Dynamics, FabFilter Pro-C 2, Waves SSL G-Master Buss Compressor, UAD Neve 33609"
        }
    elif crest_diff > 1.5:
        # Your mix is moderately too dynamic
        compression_amount = round(crest_diff * 0.6, 1)
        suggestions['crest_factor'] = {
            'action': 'add_compression',
            'amount_db': compression_amount,
            'difference': round(crest_diff, 1),
            'message': f"Your mix is {round(crest_diff, 1)}dB more dynamic than reference. Add gentle compression (2-3:1 ratio) on the mix bus with slow attack (30ms+) to bring peaks closer to the average level. Target {compression_amount}dB of gain reduction.",
            'recommended_plugins': "iZotope Ozone Dynamics, FabFilter Pro-C 2, Slate Digital FG-X, Waves API 2500"
        }
    elif crest_diff > 0.5:
        # Your mix is slightly too dynamic
        suggestions['crest_factor'] = {
            'action': 'add_light_compression',
            'difference': round(crest_diff, 1),
            'message': f"Your mix is {round(crest_diff, 1)}dB more dynamic than reference. Consider adding very gentle compression (2:1 ratio, slow attack) or subtle parallel compression to slightly reduce dynamic range.",
            'recommended_plugins': "iZotope Ozone Dynamics, FabFilter Pro-C 2, Waves CLA-76"
        }
    elif crest_diff < -3:
        # Your mix is significantly over-compressed
        suggestions['crest_factor'] = {
            'action': 'reduce_compression',
            'difference': round(abs(crest_diff), 1),
            'message': f"Your mix is {round(abs(crest_diff), 1)}dB more compressed than reference. Reduce mix bus compression/limiting significantly. Check individual track compression and ease off threshold/ratio settings. Your mix may sound squashed - aim for more breathing room.",
            'recommended_plugins': "Review settings in: iZotope Ozone Maximizer, FabFilter Pro-L 2, Waves L2/L3"
        }
    elif crest_diff < -1.5:
        # Your mix is moderately over-compressed
        suggestions['crest_factor'] = {
            'action': 'reduce_compression',
            'difference': round(abs(crest_diff), 1),
            'message': f"Your mix is {round(abs(crest_diff), 1)}dB more compressed than reference. Reduce mix bus compression by lowering ratio or raising threshold. If using a limiter, reduce gain into it or increase ceiling. This will restore some dynamic range.",
            'recommended_plugins': "Adjust: iZotope Ozone Dynamics/Maximizer, FabFilter Pro-C 2/Pro-L 2"
        }
    elif crest_diff < -0.5:
        # Your mix is slightly over-compressed
        suggestions['crest_factor'] = {
            'action': 'reduce_light_compression',
            'difference': round(abs(crest_diff), 1),
            'message': f"Your mix is {round(abs(crest_diff), 1)}dB more compressed than reference. Try slightly reducing mix bus compression (lower ratio or ease threshold) to allow a bit more dynamic variation.",
            'recommended_plugins': "Fine-tune: iZotope Ozone Dynamics, FabFilter Pro-C 2"
        }

    # Loudness/gain suggestions
    if abs(lufs_diff) > 1.0:
        gain_adjustment = round(-lufs_diff, 1)
        suggestions['gain'] = {
            'action': 'adjust_gain',
            'amount_db': gain_adjustment,
            'message': f"{'Increase' if gain_adjustment > 0 else 'Decrease'} overall level by {abs(gain_adjustment)}dB to match reference loudness",
            'recommended_plugins': "Utility/Gain plugin (stock DAW), iZotope Ozone Maximizer (for final loudness), FabFilter Pro-L 2"
        }

    # Limiting suggestions (based on peak levels)
    peak_diff = your_mix['peak_db'] - reference['peak_db']
    if peak_diff > 1:
        suggestions['limiting'] = {
            'action': 'add_limiting',
            'message': f"Your peaks are {round(peak_diff, 1)}dB higher than reference. Consider using a limiter to control peaks.",
            'recommended_plugins': "iZotope Ozone Maximizer, FabFilter Pro-L 2, Waves L2 Ultramaximizer, LoudMax (free)"
        }

    return {k: v for k, v in suggestions.items() if v is not None}
