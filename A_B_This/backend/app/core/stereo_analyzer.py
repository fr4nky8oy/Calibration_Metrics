"""
Stereo width and phase correlation analysis for A/B This
Analyzes stereo field, mid-side balance, and phase relationships
"""

from scipy import signal
import numpy as np
from typing import Dict


# Frequency bands for per-band stereo analysis
STEREO_BANDS = {
    'low_end': (20, 250),      # Should be mostly mono
    'low_mids': (250, 500),
    'mids': (500, 2000),
    'high_mids': (2000, 6000),
    'highs': (6000, 20000)
}


def analyze_stereo_width(audio: np.ndarray, sr: int) -> Dict:
    """
    Analyze stereo width and phase characteristics

    Args:
        audio: Audio samples (stereo - 2 channels)
        sr: Sample rate

    Returns:
        Dictionary with stereo analysis results
    """
    # Handle mono files
    if audio.ndim == 1:
        return {
            'is_mono': True,
            'overall_width': 0,
            'phase_correlation': 1.0,
            'per_band_width': {band: 0 for band in STEREO_BANDS},
            'assessment': 'File is mono - no stereo width'
        }

    # Ensure we have exactly 2 channels
    if audio.shape[0] != 2:
        # If more than 2 channels, use first two
        audio = audio[:2]

    left = audio[0]
    right = audio[1]

    # Extract mid and side channels
    mid = (left + right) / 2
    side = (left - right) / 2

    # Calculate overall stereo width
    overall_width = _calculate_width_percentage(mid, side)

    # Calculate phase correlation
    phase_correlation = _calculate_phase_correlation(left, right)

    # Calculate stereo width per frequency band
    per_band_width = _analyze_per_band_width(audio, sr)

    # Check for mono compatibility issues
    mono_compatible = phase_correlation > -0.5

    # Generate assessment
    assessment = _generate_stereo_assessment(
        overall_width,
        phase_correlation,
        per_band_width
    )

    return {
        'is_mono': False,
        'overall_width': round(overall_width, 1),
        'phase_correlation': round(phase_correlation, 3),
        'per_band_width': per_band_width,
        'mono_compatible': mono_compatible,
        'assessment': assessment
    }


def _calculate_width_percentage(mid: np.ndarray, side: np.ndarray) -> float:
    """
    Calculate stereo width as percentage based on mid/side energy ratio

    Args:
        mid: Mid channel (L+R)/2
        side: Side channel (L-R)/2

    Returns:
        Width percentage (0 = mono, 100 = very wide)
    """
    mid_energy = np.sum(mid**2)
    side_energy = np.sum(side**2)
    total_energy = mid_energy + side_energy

    if total_energy < 1e-10:
        return 0.0

    # Calculate width: higher side energy = wider
    width_ratio = side_energy / total_energy
    width_percentage = width_ratio * 100

    return float(width_percentage)


def _calculate_phase_correlation(left: np.ndarray, right: np.ndarray) -> float:
    """
    Calculate phase correlation between left and right channels

    Args:
        left: Left channel
        right: Right channel

    Returns:
        Correlation coefficient (-1 to +1)
        +1 = perfectly in phase (mono)
        0 = uncorrelated (wide stereo)
        -1 = perfectly out of phase (mono compatibility issues)
    """
    # Normalize to prevent overflow
    left_norm = left - np.mean(left)
    right_norm = right - np.mean(right)

    # Calculate correlation
    correlation = np.corrcoef(left_norm, right_norm)[0, 1]

    return float(correlation)


def _analyze_per_band_width(audio: np.ndarray, sr: int) -> Dict:
    """
    Analyze stereo width per frequency band

    Args:
        audio: Stereo audio (2 channels)
        sr: Sample rate

    Returns:
        Dictionary with width per band
    """
    left = audio[0]
    right = audio[1]

    per_band_width = {}
    nyquist = sr / 2

    for band_name, (low, high) in STEREO_BANDS.items():
        # Cap frequency at Nyquist
        high_capped = min(high, nyquist - 100)

        # Skip if band is above Nyquist
        if low >= nyquist:
            per_band_width[band_name] = {
                'width': 0.0,
                'frequency_range': f"{low}-{high}Hz (above Nyquist)"
            }
            continue

        # Bandpass filter both channels
        sos = signal.butter(4, [low, high_capped], btype='band', fs=sr, output='sos')
        left_filtered = signal.sosfilt(sos, left)
        right_filtered = signal.sosfilt(sos, right)

        # Extract mid and side for this band
        mid_band = (left_filtered + right_filtered) / 2
        side_band = (left_filtered - right_filtered) / 2

        # Calculate width for this band
        width = _calculate_width_percentage(mid_band, side_band)

        per_band_width[band_name] = {
            'width': round(width, 1),
            'frequency_range': f"{low}-{high}Hz"
        }

    return per_band_width


def _generate_stereo_assessment(
    overall_width: float,
    phase_correlation: float,
    per_band_width: Dict
) -> str:
    """Generate human-readable assessment of stereo characteristics"""

    assessments = []

    # Overall width assessment
    if overall_width < 20:
        assessments.append("Very narrow stereo image (mostly mono)")
    elif overall_width < 40:
        assessments.append("Narrow stereo image")
    elif overall_width < 60:
        assessments.append("Moderate stereo width")
    elif overall_width < 80:
        assessments.append("Wide stereo image")
    else:
        assessments.append("Very wide stereo image")

    # Phase correlation assessment
    if phase_correlation < -0.5:
        assessments.append("⚠️ Severe phase issues - will cancel out in mono")
    elif phase_correlation < 0:
        assessments.append("⚠️ Some phase issues - check mono compatibility")
    elif phase_correlation > 0.9:
        assessments.append("Mostly mono content")

    # Low-end width check
    low_end_width = per_band_width.get('low_end', {}).get('width', 0)
    if low_end_width > 50:
        assessments.append("⚠️ Low end is too wide - should be centered for power")
    elif low_end_width < 30:
        assessments.append("✅ Low end is properly centered")

    return ". ".join(assessments)


def compare_stereo_width(
    your_mix_stereo: Dict,
    reference_stereo: Dict
) -> Dict:
    """
    Compare stereo characteristics between two tracks

    Args:
        your_mix_stereo: Stereo analysis from analyze_stereo_width()
        reference_stereo: Stereo analysis from analyze_stereo_width()

    Returns:
        Comparison results with suggestions
    """
    # Handle mono files
    if your_mix_stereo['is_mono'] and reference_stereo['is_mono']:
        return {
            'both_mono': True,
            'message': 'Both files are mono - no stereo comparison possible'
        }

    if your_mix_stereo['is_mono']:
        return {
            'your_mix_mono': True,
            'message': 'Your mix is mono while reference is stereo - consider adding stereo width'
        }

    if reference_stereo['is_mono']:
        return {
            'reference_mono': True,
            'message': 'Reference is mono - stereo comparison not applicable'
        }

    # Calculate differences
    width_diff = your_mix_stereo['overall_width'] - reference_stereo['overall_width']
    phase_diff = your_mix_stereo['phase_correlation'] - reference_stereo['phase_correlation']

    # Compare per-band widths
    band_comparisons = {}
    problem_bands = []

    for band_name in STEREO_BANDS:
        your_width = your_mix_stereo['per_band_width'][band_name]['width']
        ref_width = reference_stereo['per_band_width'][band_name]['width']
        diff = your_width - ref_width

        band_comparisons[band_name] = {
            'your_width': your_width,
            'reference_width': ref_width,
            'difference': round(diff, 1),
            'status': 'wider' if diff > 10 else 'narrower' if diff < -10 else 'similar'
        }

        # Flag significant differences
        if abs(diff) > 15:
            severity = 'high' if abs(diff) > 30 else 'moderate'
            problem_bands.append({
                'band': band_name,
                'your_width': your_width,
                'reference_width': ref_width,
                'difference': round(diff, 1),
                'severity': severity
            })

    # Generate suggestions
    suggestions = _generate_stereo_suggestions(
        width_diff,
        phase_diff,
        problem_bands,
        your_mix_stereo,
        reference_stereo
    )

    return {
        'both_mono': False,
        'overall_width_difference': round(width_diff, 1),
        'phase_correlation_difference': round(phase_diff, 3),
        'band_comparisons': band_comparisons,
        'problem_bands': problem_bands,
        'suggestions': suggestions,
        'assessment': _generate_comparison_assessment(width_diff, phase_diff, problem_bands)
    }


def _generate_stereo_suggestions(
    width_diff: float,
    phase_diff: float,
    problem_bands: list,
    your_mix: Dict,
    reference: Dict
) -> Dict:
    """Generate actionable stereo width suggestions"""

    suggestions = {
        'overall': None,
        'per_band': [],
        'phase': None
    }

    # Overall width suggestions
    if width_diff < -15:
        suggestions['overall'] = {
            'action': 'widen',
            'amount': f"{abs(width_diff):.1f}%",
            'message': f"Your mix is {abs(width_diff):.1f}% narrower than reference. Consider using stereo widener or mid-side processing."
        }
    elif width_diff > 15:
        suggestions['overall'] = {
            'action': 'narrow',
            'amount': f"{width_diff:.1f}%",
            'message': f"Your mix is {width_diff:.1f}% wider than reference. Consider reducing stereo enhancement or check for phase issues."
        }

    # Per-band suggestions
    for problem in problem_bands:
        band_name = problem['band']
        diff = problem['difference']

        if band_name == 'low_end':
            if diff > 0:
                suggestions['per_band'].append({
                    'band': band_name,
                    'message': f"Low end is {diff:.1f}% too wide. Use mid-side EQ to make bass/kick more mono for better power and punch."
                })
        elif diff > 15:
            suggestions['per_band'].append({
                'band': band_name,
                'message': f"{band_name.replace('_', ' ').title()} is {diff:.1f}% wider. Consider narrowing this range slightly."
            })
        elif diff < -15:
            suggestions['per_band'].append({
                'band': band_name,
                'message': f"{band_name.replace('_', ' ').title()} is {abs(diff):.1f}% narrower. Consider widening this range for more spaciousness."
            })

    # Phase correlation suggestions
    if your_mix['phase_correlation'] < -0.5:
        suggestions['phase'] = {
            'severity': 'critical',
            'message': "⚠️ Critical phase issues detected. Mix will collapse in mono. Check for out-of-phase stereo processing."
        }
    elif your_mix['phase_correlation'] < 0 and reference['phase_correlation'] > 0:
        suggestions['phase'] = {
            'severity': 'warning',
            'message': "⚠️ Your mix has phase issues that reference doesn't. Check stereo wideners and verify mono compatibility."
        }

    return suggestions


def _generate_comparison_assessment(
    width_diff: float,
    phase_diff: float,
    problem_bands: list
) -> str:
    """Generate overall comparison assessment"""

    if abs(width_diff) < 10 and abs(phase_diff) < 0.2 and len(problem_bands) == 0:
        return "Your mix has similar stereo characteristics to the reference - good balance!"

    assessments = []

    if abs(width_diff) > 20:
        if width_diff > 0:
            assessments.append(f"Your mix is significantly wider ({width_diff:.1f}% more)")
        else:
            assessments.append(f"Your mix is significantly narrower ({abs(width_diff):.1f}% less)")

    if len(problem_bands) > 0:
        assessments.append(f"{len(problem_bands)} frequency band(s) have mismatched width")

    if abs(phase_diff) > 0.3:
        assessments.append("Phase correlation differs notably from reference")

    return ". ".join(assessments) if assessments else "Minor stereo differences from reference"
