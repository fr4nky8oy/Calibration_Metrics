"""
Frequency spectrum analysis for A/B This
Analyzes frequency balance across 6 standard mixing bands
"""

from scipy import signal
import numpy as np
from typing import Dict, List, Tuple


# Standard mixing bands
FREQUENCY_BANDS = {
    'sub_bass': (20, 60),
    'bass': (60, 250),
    'low_mids': (250, 500),
    'mids': (500, 2000),
    'high_mids': (2000, 6000),
    'highs': (6000, 20000)
}

# Center frequencies for EQ suggestions
BAND_CENTER_FREQS = {
    'sub_bass': 40,
    'bass': 120,
    'low_mids': 350,
    'mids': 1000,
    'high_mids': 3500,
    'highs': 10000
}


def analyze_frequency_balance(audio: np.ndarray, sr: int) -> Dict:
    """
    Analyze RMS levels across 6 standard mixing bands

    Args:
        audio: Audio samples (mono)
        sr: Sample rate

    Returns:
        Dictionary with band analysis results
    """
    results = {}
    total_energy = 0

    # Calculate Nyquist frequency
    nyquist = sr / 2

    for band_name, (low, high) in FREQUENCY_BANDS.items():
        # Cap high frequency at Nyquist - 100Hz for safety
        high_capped = min(high, nyquist - 100)

        # Skip band if it's entirely above Nyquist
        if low >= nyquist:
            results[band_name] = {
                'level_db': -80.0,
                'energy': 0.0,
                'frequency_range': f"{low}-{high}Hz (above Nyquist)"
            }
            continue

        # Design 4th-order Butterworth bandpass filter
        sos = signal.butter(4, [low, high_capped], btype='band', fs=sr, output='sos')

        # Apply filter
        filtered = signal.sosfilt(sos, audio)

        # Calculate RMS in dB
        rms = np.sqrt(np.mean(filtered**2))
        level_db = 20 * np.log10(rms + 1e-10)

        # Calculate energy for percentage calculation
        energy = np.sum(filtered**2)
        total_energy += energy

        results[band_name] = {
            'level_db': round(float(level_db), 1),
            'energy': float(energy),
            'frequency_range': f"{low}-{high}Hz"
        }

    # Calculate energy percentages
    for band_name in results:
        energy_percent = (results[band_name]['energy'] / total_energy) * 100
        results[band_name]['energy_percent'] = round(energy_percent, 1)
        del results[band_name]['energy']  # Remove raw energy from output

    return results


def get_spectrum_data(audio: np.ndarray, sr: int, nfft: int = 8192) -> Tuple[np.ndarray, np.ndarray]:
    """
    Get full frequency spectrum for visualization

    Args:
        audio: Audio samples (mono)
        sr: Sample rate
        nfft: FFT size

    Returns:
        Tuple of (frequencies, magnitudes in dB)
    """
    # Use Welch's method for smoother spectrum
    frequencies, psd = signal.welch(audio, sr, nperseg=nfft, scaling='spectrum')

    # Convert to dB
    magnitudes_db = 10 * np.log10(psd + 1e-10)

    # Limit to audible range (20Hz-20kHz)
    mask = (frequencies >= 20) & (frequencies <= 20000)

    return frequencies[mask], magnitudes_db[mask]


def compare_frequency_balance(
    your_mix_balance: Dict,
    reference_balance: Dict
) -> Dict:
    """
    Compare frequency balance between two tracks

    Args:
        your_mix_balance: Frequency balance from analyze_frequency_balance()
        reference_balance: Frequency balance from analyze_frequency_balance()

    Returns:
        Comparison results with differences and problem bands
    """
    differences = {}
    problem_bands = []

    for band in FREQUENCY_BANDS.keys():
        your_level = your_mix_balance[band]['level_db']
        ref_level = reference_balance[band]['level_db']
        diff = your_level - ref_level

        differences[band] = {
            'your_level': your_level,
            'reference_level': ref_level,
            'difference_db': round(diff, 1),
            'status': 'louder' if diff > 0.5 else 'quieter' if diff < -0.5 else 'matched'
        }

        # Flag problem areas (>3dB difference)
        if abs(diff) > 3:
            severity = 'high' if abs(diff) > 6 else 'moderate'

            problem_bands.append({
                'band': band,
                'frequency_range': your_mix_balance[band]['frequency_range'],
                'difference_db': round(diff, 1),
                'severity': severity,
                'suggestion': _generate_eq_suggestion(band, diff)
            })

    return {
        'differences': differences,
        'problem_bands': problem_bands
    }


def _generate_eq_suggestion(band: str, difference_db: float) -> Dict:
    """
    Generate actionable EQ advice based on frequency difference

    Args:
        band: Band name
        difference_db: Difference in dB (positive = your mix is louder)

    Returns:
        EQ suggestion dictionary
    """
    freq = BAND_CENTER_FREQS[band]

    if difference_db > 0:
        # Your mix is louder - need to cut
        gain = round(-difference_db * 0.7, 1)  # Cut ~70% of difference
        return {
            'type': 'cut',
            'frequency': freq,
            'gain_db': gain,
            'q': 1.0,
            'message': f"Cut {freq}Hz by {gain}dB to match reference"
        }
    else:
        # Your mix is quieter - need to boost
        gain = round(-difference_db * 0.7, 1)
        return {
            'type': 'boost',
            'frequency': freq,
            'gain_db': gain,
            'q': 1.0,
            'message': f"Boost {freq}Hz by {gain}dB to match reference"
        }
