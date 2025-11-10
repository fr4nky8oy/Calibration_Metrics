"""
Frequency masking analysis for A/B This
Detects overlapping frequency content and cluttered bands
"""

from scipy import signal
import numpy as np
from typing import Dict, List


# Critical bands (simplified Bark scale)
CRITICAL_BANDS = [
    (20, 100, "Sub Bass"),
    (100, 200, "Bass Fundamentals"),
    (200, 400, "Low Mids / Mud Zone"),
    (400, 600, "Low-Mid Body"),
    (600, 1000, "Mid Clarity"),
    (1000, 2000, "Vocal Presence"),
    (2000, 3000, "High Mids Clarity"),
    (3000, 4000, "Articulation"),
    (4000, 6000, "Brightness"),
    (6000, 10000, "Air"),
    (10000, 20000, "Sparkle")
]


def analyze_frequency_masking(audio: np.ndarray, sr: int) -> Dict:
    """
    Detect frequency masking by analyzing energy concentration in overlapping critical bands

    Args:
        audio: Audio samples (mono)
        sr: Sample rate

    Returns:
        Dictionary with masking analysis results
    """
    band_energies = []

    # Calculate Nyquist frequency
    nyquist = sr / 2

    # Calculate energy in each critical band
    for low, high, name in CRITICAL_BANDS:
        # Cap high frequency at Nyquist - 100Hz
        high_capped = min(high, nyquist - 100)

        # Skip band if entirely above Nyquist
        if low >= nyquist:
            continue

        # Bandpass filter
        sos = signal.butter(4, [low, high_capped], btype='band', fs=sr, output='sos')
        filtered = signal.sosfilt(sos, audio)

        # Calculate RMS energy in dB
        rms = np.sqrt(np.mean(filtered**2))
        energy_db = 20 * np.log10(rms + 1e-10)

        # Calculate spectral flatness (measure of tonal vs noisy content)
        # Low flatness = single frequency dominates (good separation)
        # High flatness = many frequencies (potential masking)
        spectrum = np.abs(np.fft.rfft(filtered))
        geometric_mean = np.exp(np.mean(np.log(spectrum + 1e-10)))
        arithmetic_mean = np.mean(spectrum)
        flatness = geometric_mean / (arithmetic_mean + 1e-10)

        band_energies.append({
            'name': name,
            'range': f"{low}-{high}Hz",
            'energy_db': round(float(energy_db), 1),
            'spectral_flatness': round(float(flatness), 3),
            'low': low,
            'high': high
        })

    # Detect masking issues
    masking_issues = []

    for i in range(len(band_energies) - 1):
        current = band_energies[i]
        next_band = band_energies[i + 1]

        # Check if adjacent bands have similar high energy (masking)
        energy_diff = abs(current['energy_db'] - next_band['energy_db'])

        # Both bands loud + similar energy = potential masking
        if current['energy_db'] > -20 and next_band['energy_db'] > -20:
            if energy_diff < 3:  # Less than 3dB separation
                severity = "high" if current['energy_db'] > -15 else "moderate"

                masking_issues.append({
                    'bands': f"{current['name']} + {next_band['name']}",
                    'frequency_range': f"{current['low']}-{next_band['high']}Hz",
                    'issue': 'overlapping_energy',
                    'severity': severity,
                    'energy_current': current['energy_db'],
                    'energy_next': next_band['energy_db'],
                    'separation_db': round(energy_diff, 1),
                    'message': f"High energy overlap between {current['range']} and {next_band['range']}"
                })

    # Calculate overall clarity score (0-100)
    # Higher score = better frequency separation
    clarity_score = 0
    for i in range(len(band_energies) - 1):
        separation = abs(band_energies[i]['energy_db'] - band_energies[i + 1]['energy_db'])
        clarity_score += min(separation, 10)  # Cap at 10dB contribution

    # Normalize to 0-100 scale
    clarity_score = int((clarity_score / (len(band_energies) - 1)) * 10)
    clarity_score = min(100, max(0, clarity_score))  # Clamp to 0-100

    return {
        'band_energies': band_energies,
        'masking_issues': masking_issues,
        'clarity_score': clarity_score
    }


def compare_masking(
    your_mix_masking: Dict,
    reference_masking: Dict
) -> Dict:
    """
    Compare masking between your mix and reference

    Args:
        your_mix_masking: Masking analysis from analyze_frequency_masking()
        reference_masking: Masking analysis from analyze_frequency_masking()

    Returns:
        Comparison results with suggestions
    """
    your_issues = your_mix_masking['masking_issues']
    ref_issues = reference_masking['masking_issues']

    # Generate suggestions for issues unique to your mix
    suggestions = []

    for issue in your_issues:
        # Check if reference has same issue
        ref_has_issue = any(
            ri['frequency_range'] == issue['frequency_range']
            for ri in ref_issues
        )

        if not ref_has_issue:
            # Your mix has masking that reference doesn't
            suggestions.append({
                'issue': issue['bands'],
                'frequency': issue['frequency_range'],
                'suggestion': f"Reduce energy in one of these ranges to create separation. Reference keeps these bands distinct.",
                'severity': issue['severity']
            })

    # Calculate clarity difference
    clarity_diff = your_mix_masking['clarity_score'] - reference_masking['clarity_score']

    return {
        'your_mix_clarity': your_mix_masking['clarity_score'],
        'reference_clarity': reference_masking['clarity_score'],
        'clarity_difference': clarity_diff,
        'your_issues_count': len(your_issues),
        'reference_issues_count': len(ref_issues),
        'suggestions': suggestions,
        'assessment': _generate_clarity_assessment(clarity_diff, len(your_issues), len(ref_issues))
    }


def _generate_clarity_assessment(
    clarity_diff: int,
    your_issues_count: int,
    ref_issues_count: int
) -> str:
    """Generate human-readable assessment of clarity comparison"""

    if clarity_diff >= 10:
        return "Your mix has excellent frequency separation - better than the reference!"
    elif clarity_diff >= 0:
        return "Your mix has similar frequency separation to the reference."
    elif clarity_diff >= -10:
        return "Your mix has slightly more frequency overlap than the reference."
    elif clarity_diff >= -20:
        return "Your mix has noticeably more frequency masking than the reference. Consider carving out space for individual elements."
    else:
        return "Your mix has significant frequency masking issues compared to the reference. Focus on creating separation between instruments."
