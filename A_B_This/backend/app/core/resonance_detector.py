"""
Resonance detection for A/B This
Identifies narrow frequency peaks that may cause harshness or problems
"""

from scipy import signal
import numpy as np
from typing import Dict, List


def detect_resonances(audio: np.ndarray, sr: int, nfft: int = 8192) -> List[Dict]:
    """
    Detect resonant frequencies using peak finding on spectrum

    Args:
        audio: Audio samples (mono)
        sr: Sample rate
        nfft: FFT size for analysis

    Returns:
        List of detected resonances with frequency, level, and severity
    """
    # Adjust FFT size for short files
    nfft_actual = min(nfft, len(audio))

    # Get frequency spectrum using Welch's method
    frequencies, psd = signal.welch(audio, sr, nperseg=nfft_actual, scaling='spectrum')

    # Convert to dB
    magnitude_db = 10 * np.log10(psd + 1e-10)

    # Only analyze audible range (20Hz-20kHz, but also cap at Nyquist)
    nyquist = sr / 2
    mask = (frequencies >= 20) & (frequencies <= min(20000, nyquist))
    frequencies = frequencies[mask]
    magnitude_db = magnitude_db[mask]

    # Calculate minimum distance (at least 1)
    distance = max(1, int(len(frequencies) / 200))

    # Find peaks with prominence threshold
    peaks, properties = signal.find_peaks(
        magnitude_db,
        prominence=3,      # Minimum 3dB prominence above neighbors
        height=-40,        # Must be above -40dB
        distance=distance  # At least ~100Hz apart
    )

    resonances = []

    for i, peak_idx in enumerate(peaks):
        freq = frequencies[peak_idx]
        level = magnitude_db[peak_idx]
        prominence = properties['prominences'][i]  # Use enumeration index, not peak_idx

        # Estimate Q-factor (sharpness of peak)
        q_factor = _estimate_q_factor(magnitude_db, peak_idx, frequencies)

        # Classify severity based on prominence and Q-factor
        severity = _classify_resonance_severity(prominence, q_factor, freq)

        resonances.append({
            'frequency': round(float(freq), 1),
            'level': round(float(level), 1),
            'prominence': round(float(prominence), 1),
            'q_factor': round(q_factor, 1),
            'severity': severity
        })

    # Sort by severity (high first) then by prominence
    severity_order = {'high': 0, 'moderate': 1, 'low': 2}
    resonances.sort(key=lambda x: (severity_order[x['severity']], -x['prominence']))

    return resonances


def _estimate_q_factor(magnitude_db: np.ndarray, peak_idx: int, frequencies: np.ndarray) -> float:
    """
    Estimate Q-factor of a resonance peak
    Higher Q = sharper/narrower peak

    Args:
        magnitude_db: Magnitude spectrum in dB
        peak_idx: Index of the peak
        frequencies: Frequency array

    Returns:
        Estimated Q-factor
    """
    peak_level = magnitude_db[peak_idx]
    peak_freq = frequencies[peak_idx]

    # Find -3dB points (half-power points)
    target_level = peak_level - 3

    # Search left for -3dB point
    left_idx = peak_idx
    while left_idx > 0 and magnitude_db[left_idx] > target_level:
        left_idx -= 1

    # Search right for -3dB point
    right_idx = peak_idx
    while right_idx < len(magnitude_db) - 1 and magnitude_db[right_idx] > target_level:
        right_idx += 1

    # Calculate bandwidth
    if left_idx > 0 and right_idx < len(magnitude_db) - 1:
        bandwidth = frequencies[right_idx] - frequencies[left_idx]

        if bandwidth > 0:
            q_factor = peak_freq / bandwidth
            return min(q_factor, 20.0)  # Cap at 20 for very sharp peaks

    # Default Q if calculation fails
    return 1.0


def _classify_resonance_severity(prominence: float, q_factor: float, frequency: float) -> str:
    """
    Classify resonance severity based on prominence, Q-factor, and frequency

    Args:
        prominence: Peak prominence in dB
        q_factor: Estimated Q-factor
        frequency: Frequency in Hz

    Returns:
        Severity classification: 'high', 'moderate', or 'low'
    """
    # Harsh frequency ranges (more problematic)
    harsh_ranges = [
        (2000, 4000),   # Presence harshness
        (6000, 8000),   # Sibilance
    ]

    is_harsh_range = any(low <= frequency <= high for low, high in harsh_ranges)

    # High severity: prominent + sharp peak
    if prominence >= 6 and q_factor >= 2:
        return 'high'

    # High severity: very prominent in harsh range
    if prominence >= 5 and is_harsh_range:
        return 'high'

    # Moderate severity: noticeable peak
    if prominence >= 4 or (prominence >= 3 and q_factor >= 2):
        return 'moderate'

    # Low severity: minor peak
    return 'low'


def compare_resonances(
    your_mix_resonances: List[Dict],
    reference_resonances: List[Dict]
) -> Dict:
    """
    Compare resonances between your mix and reference

    Args:
        your_mix_resonances: Resonances from detect_resonances()
        reference_resonances: Resonances from detect_resonances()

    Returns:
        Comparison results with suggestions
    """
    # Find problematic resonances unique to your mix
    problem_resonances = []

    for your_res in your_mix_resonances:
        # Check if reference has similar resonance (within 50Hz)
        ref_has_similar = any(
            abs(ref_res['frequency'] - your_res['frequency']) < 50
            for ref_res in reference_resonances
        )

        if not ref_has_similar and your_res['severity'] in ['high', 'moderate']:
            # Your mix has resonance that reference doesn't
            suggestion = _generate_cut_suggestion(
                your_res['frequency'],
                your_res['prominence'],
                your_res['q_factor']
            )

            problem_resonances.append({
                'frequency': your_res['frequency'],
                'level': your_res['level'],
                'prominence': your_res['prominence'],
                'severity': your_res['severity'],
                'suggestion': suggestion
            })

    # Count resonances by severity
    your_high = sum(1 for r in your_mix_resonances if r['severity'] == 'high')
    your_moderate = sum(1 for r in your_mix_resonances if r['severity'] == 'moderate')
    ref_high = sum(1 for r in reference_resonances if r['severity'] == 'high')
    ref_moderate = sum(1 for r in reference_resonances if r['severity'] == 'moderate')

    return {
        'your_mix_total': len(your_mix_resonances),
        'reference_total': len(reference_resonances),
        'your_high_severity': your_high,
        'your_moderate_severity': your_moderate,
        'reference_high_severity': ref_high,
        'reference_moderate_severity': ref_moderate,
        'problem_resonances': problem_resonances,
        'assessment': _generate_resonance_assessment(
            len(your_mix_resonances),
            len(reference_resonances),
            your_high,
            ref_high
        )
    }


def _generate_cut_suggestion(frequency: float, prominence: float, q_factor: float) -> Dict:
    """Generate EQ cut suggestion for a resonance"""

    # Adjust gain based on prominence
    gain = -min(prominence * 0.8, 8.0)  # Cut up to -8dB

    # Adjust Q based on peak sharpness
    suggested_q = min(q_factor * 0.8, 5.0)  # Use narrower Q than the peak

    return {
        'type': 'cut',
        'frequency': int(frequency),
        'gain_db': round(gain, 1),
        'q': round(suggested_q, 1),
        'message': f"Cut {int(frequency)}Hz by {round(gain, 1)}dB (Q={round(suggested_q, 1)}) to reduce {_describe_frequency_range(frequency)}"
    }


def _describe_frequency_range(frequency: float) -> str:
    """Describe what a frequency range typically affects"""

    if frequency < 100:
        return "rumble/sub-bass resonance"
    elif frequency < 250:
        return "bass resonance"
    elif frequency < 500:
        return "mud/boxiness"
    elif frequency < 1000:
        return "low-mid resonance"
    elif frequency < 2000:
        return "mid-range resonance"
    elif frequency < 4000:
        return "presence harshness"
    elif frequency < 8000:
        return "sibilance/brightness"
    else:
        return "high-frequency harshness"


def _generate_resonance_assessment(
    your_total: int,
    ref_total: int,
    your_high: int,
    ref_high: int
) -> str:
    """Generate human-readable assessment of resonance comparison"""

    if your_high == 0 and your_total <= ref_total:
        return "Your mix has a smooth frequency response - no significant resonances detected!"
    elif your_high == 0:
        return "Your mix has no severe resonances, similar to the reference."
    elif your_high <= ref_high:
        return "Your mix has a similar number of resonances as the reference."
    elif your_high <= ref_high + 2:
        return "Your mix has slightly more resonances than the reference. Consider smoothing the frequency response."
    else:
        return "Your mix has significantly more resonances than the reference. Focus on reducing harsh peaks for a smoother sound."
