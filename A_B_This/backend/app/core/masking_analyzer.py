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
            # Generate specific suggestions based on frequency band
            specific_suggestion = _generate_masking_fix_suggestion(issue)

            suggestions.append({
                'bands': issue['bands'].split(' + '),  # Split into array for easier display
                'frequency': issue['frequency_range'],
                'message': specific_suggestion['message'],
                'technique': specific_suggestion['technique'],
                'severity': issue['severity'],
                'recommended_plugins': specific_suggestion['recommended_plugins']
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


def _generate_masking_fix_suggestion(issue: Dict) -> Dict:
    """
    Generate specific, actionable suggestions for fixing frequency masking
    based on the frequency bands involved

    Args:
        issue: Dictionary with masking issue details including bands and frequency range

    Returns:
        Dictionary with message, technique, and recommended plugins
    """
    bands = issue['bands']
    freq_range = issue['frequency_range']

    # Map band names to specific mixing advice
    masking_techniques = {
        'Sub Bass + Bass Fundamentals': {
            'message': 'Sub bass and bass fundamentals are competing. Use high-pass filters to separate kick and bass, keeping kick centered below 60Hz and bass above.',
            'technique': 'HPF bass at 40-60Hz, cut kick at 80-120Hz where bass sits, or use sidechain compression. Consider multiband sidechain techniques for frequency-specific ducking.',
            'plugins': 'Wavesfactory Trackspacer, iDX Intelligent Dynamics, FabFilter Pro-Q 3, iZotope Neutron EQ'
        },
        'Bass Fundamentals + Low Mids / Mud Zone': {
            'message': 'Bass bleeding into low-mids creates muddiness. Cut 200-400Hz on bass to make room for guitars/keys.',
            'technique': 'Cut 200-300Hz on bass (2-4dB), boost same range slightly on rhythm instruments for clarity. Consider multiband sidechain to dynamically duck bass when other instruments play.',
            'plugins': 'Wavesfactory Trackspacer, iDX Intelligent Dynamics, FabFilter Pro-Q 3, iZotope Neutron EQ'
        },
        'Low Mids / Mud Zone + Low-Mid Body': {
            'message': 'The "mud zone" is cluttered. This is the most common masking problem. Use subtractive EQ to carve space.',
            'technique': 'Cut 250-400Hz on competing elements. Identify the most important element and cut others in this range. Consider multiband sidechain techniques for dynamic control.',
            'plugins': 'Wavesfactory Trackspacer, iDX Intelligent Dynamics, Oeksound Soothe2, FabFilter Pro-Q 3, iZotope Neutron EQ'
        },
        'Low-Mid Body + Mid Clarity': {
            'message': 'Low-mids competing with mid clarity. Thin out body frequencies on background elements.',
            'technique': 'HPF non-essential tracks at 200-300Hz, cut 400-600Hz on rhythm guitars/pads. Use multiband sidechain to create dynamic space.',
            'plugins': 'Wavesfactory Trackspacer, iDX Intelligent Dynamics, FabFilter Pro-Q 3, iZotope Neutron EQ'
        },
        'Mid Clarity + Vocal Presence': {
            'message': 'Instruments masking vocal presence. Cut 1-2kHz on instruments to create vocal space.',
            'technique': 'Notch cut at vocal fundamental frequency on guitars/keys, boost 1-3kHz on vocals. Consider multiband sidechain techniques to duck instruments when vocals are present.',
            'plugins': 'Wavesfactory Trackspacer, iDX Intelligent Dynamics, Oeksound Soothe2, FabFilter Pro-Q 3, iZotope Neutron EQ'
        },
        'Vocal Presence + High Mids Clarity': {
            'message': 'Vocal presence competing with high-mid instruments. Use dynamic EQ or automation.',
            'technique': 'Side-chain dynamic EQ: duck 2-4kHz on instruments when vocals are present. Multiband sidechain is ideal for this application.',
            'plugins': 'Wavesfactory Trackspacer, iDX Intelligent Dynamics, Oeksound Soothe2, iZotope Neutron (Masking Meter), FabFilter Pro-Q 3'
        },
        'High Mids Clarity + Articulation': {
            'message': 'Consonants and articulation are masked. Reduce 3-4kHz on instruments, preserve on vocals.',
            'technique': 'Cut 3-4kHz on dense instruments (synths, guitars), boost 3.5kHz on vocals for clarity. Use dynamic processing to tame resonances.',
            'plugins': 'Oeksound Soothe2, Wavesfactory Trackspacer, iDX Intelligent Dynamics, FabFilter Pro-Q 3'
        },
        'Articulation + Brightness': {
            'message': 'Too much energy in upper-mids. De-ess vocals and tame harsh instruments.',
            'technique': 'De-ess vocals at 5-7kHz, cut 4-6kHz on harsh synths/guitars. Use dynamic resonance suppression for problem frequencies.',
            'plugins': 'Oeksound Soothe2, FabFilter Pro-DS, Waves Renaissance DeEsser, iZotope Neutron EQ'
        },
        'Brightness + Air': {
            'message': 'High frequencies are congested. Use shelving EQ to control excessive brightness.',
            'technique': 'HPF non-essential elements above 8kHz, use gentle high-shelf cut on busy mixes. Dynamic resonance control helps tame harshness.',
            'plugins': 'Oeksound Soothe2, FabFilter Pro-Q 3, iZotope Ozone EQ'
        },
        'Air + Sparkle': {
            'message': 'Extreme highs are competing. Preserve air only on key elements (vocals, cymbals).',
            'technique': 'HPF most tracks above 10kHz, keep sparkle only on vocals, overheads, and featured instruments. Use dynamic processing to control excessive sibilance.',
            'plugins': 'Oeksound Soothe2, FabFilter Pro-Q 3, iZotope Ozone EQ'
        }
    }

    # Get specific advice or provide generic advice
    advice = masking_techniques.get(bands, {
        'message': f'Overlapping energy between {bands}. Create separation by reducing one frequency range.',
        'technique': 'Use EQ to cut competing frequencies on less important elements, or use dynamic EQ to duck when conflicts occur. Consider multiband sidechain techniques for frequency-specific control.',
        'plugins': 'Wavesfactory Trackspacer, iDX Intelligent Dynamics, Oeksound Soothe2, FabFilter Pro-Q 3, iZotope Neutron EQ'
    })

    return {
        'message': advice['message'],
        'technique': advice['technique'],
        'recommended_plugins': advice['plugins']
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
