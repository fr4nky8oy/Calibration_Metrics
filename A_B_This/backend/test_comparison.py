"""
Test script for A/B This comparison
Tests the analysis modules with sample audio files
"""

import sys
from pathlib import Path
import json

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.comparator import compare_audio_files


def test_comparison():
    """Test comparison with sample audio files"""

    # Try to find audio files - first check CalibrationMetrics folder
    audio_folder = Path(__file__).parent.parent.parent / "audio_files"

    audio_files = []
    if audio_folder.exists():
        audio_files = list(audio_folder.glob("*.wav")) + list(audio_folder.glob("*.mp3"))

    # If not found, use scipy test files (only standard formats)
    if len(audio_files) < 2:
        scipy_test_folder = Path(__file__).parent / "venv/lib/python3.13/site-packages/scipy/io/tests/data"
        if scipy_test_folder.exists():
            # Only use standard WAV files
            standard_files = [
                scipy_test_folder / "test-44100Hz-2ch-32bit-float-le.wav",
                scipy_test_folder / "test-44100Hz-le-1ch-4bytes.wav"
            ]
            audio_files = [f for f in standard_files if f.exists()]

    if len(audio_files) < 2:
        print(f"Need at least 2 audio files in {audio_folder}")
        print(f"Found: {len(audio_files)} files")
        return

    your_mix = str(audio_files[0])
    reference = str(audio_files[1])

    print(f"\n{'='*60}")
    print(f"A/B This - Comparison Test")
    print(f"{'='*60}\n")
    print(f"Your Mix:   {Path(your_mix).name}")
    print(f"Reference:  {Path(reference).name}")
    print(f"\nAnalyzing...\n")

    try:
        # Run comparison
        results = compare_audio_files(your_mix, reference, downsample_sr=22050)

        print(f"\n{'='*60}")
        print(f"RESULTS")
        print(f"{'='*60}\n")

        print(f"Processing Time: {results['processing_time']}s\n")

        # Your Mix Summary
        print(f"YOUR MIX ({results['your_mix']['filename']}):")
        print(f"  Duration: {results['your_mix']['duration']}s")
        print(f"  Format: {results['your_mix']['format']}")
        print(f"  LUFS: {results['your_mix']['dynamics']['lufs_integrated']} LUFS")
        print(f"  RMS: {results['your_mix']['dynamics']['rms_db']} dB")
        print(f"  Clarity Score: {results['your_mix']['masking']['clarity_score']}/100")
        print(f"  Resonances: {len(results['your_mix']['resonances'])}")

        # Reference Summary
        print(f"\nREFERENCE ({results['reference']['filename']}):")
        print(f"  Duration: {results['reference']['duration']}s")
        print(f"  Format: {results['reference']['format']}")
        print(f"  LUFS: {results['reference']['dynamics']['lufs_integrated']} LUFS")
        print(f"  RMS: {results['reference']['dynamics']['rms_db']} dB")
        print(f"  Clarity Score: {results['reference']['masking']['clarity_score']}/100")
        print(f"  Resonances: {len(results['reference']['resonances'])}")

        # Frequency Balance Comparison
        print(f"\nFREQUENCY BALANCE COMPARISON:")
        for band, diff_data in results['comparison']['frequency_balance']['differences'].items():
            diff = diff_data['difference_db']
            status = diff_data['status']
            symbol = "⬆️" if status == "louder" else "⬇️" if status == "quieter" else "≈"
            print(f"  {band:12s}: {diff:+5.1f} dB {symbol}")

        # Problem Bands
        problem_bands = results['comparison']['frequency_balance']['problem_bands']
        if problem_bands:
            print(f"\nPROBLEM BANDS:")
            for problem in problem_bands:
                print(f"  {problem['band']:12s}: {problem['difference_db']:+5.1f} dB ({problem['severity']})")
                print(f"    → {problem['suggestion']['message']}")

        # Masking Comparison
        print(f"\nMASKING ANALYSIS:")
        masking_comp = results['comparison']['masking']
        print(f"  Your Mix Clarity:  {masking_comp['your_mix_clarity']}/100")
        print(f"  Reference Clarity: {masking_comp['reference_clarity']}/100")
        print(f"  Difference:        {masking_comp['clarity_difference']:+d}")
        print(f"  Assessment: {masking_comp['assessment']}")

        # Resonances
        print(f"\nRESONANCE COMPARISON:")
        res_comp = results['comparison']['resonances']
        print(f"  Your Mix High Severity:  {res_comp['your_high_severity']}")
        print(f"  Reference High Severity: {res_comp['reference_high_severity']}")

        if res_comp['problem_resonances']:
            print(f"\n  Problem Resonances:")
            for res in res_comp['problem_resonances'][:5]:  # Show top 5
                print(f"    {res['frequency']:7.1f} Hz - {res['severity']:8s} - {res['suggestion']['message']}")

        # Dynamics Comparison
        print(f"\nDYNAMIC RANGE COMPARISON:")
        dyn_comp = results['comparison']['dynamics']
        print(f"  Compression: {dyn_comp['compression_comparison']['description']}")
        print(f"  Loudness:    {dyn_comp['loudness_comparison']['status']}")

        # Stereo Width Comparison
        print(f"\nSTEREO WIDTH COMPARISON:")
        stereo_comp = results['comparison']['stereo']

        if stereo_comp.get('both_mono'):
            print(f"  {stereo_comp.get('message', 'Both files are mono')}")
        elif stereo_comp.get('your_mix_mono') or stereo_comp.get('reference_mono'):
            print(f"  {stereo_comp.get('message', 'One file is mono')}")
        else:
            print(f"  Your Mix Overall Width:  {results['your_mix']['stereo']['overall_width']}%")
            print(f"  Reference Overall Width: {results['reference']['stereo']['overall_width']}%")
            print(f"  Difference:              {stereo_comp['overall_width_difference']:+.1f}%")
            print(f"  Phase Correlation Diff:  {stereo_comp['phase_correlation_difference']:+.3f}")
            print(f"  Assessment: {stereo_comp['assessment']}")

            # Per-band width comparison
            if stereo_comp.get('problem_bands'):
                print(f"\n  Problem Bands:")
                for pb in stereo_comp['problem_bands'][:3]:  # Show top 3
                    print(f"    {pb['band']:12s}: Your {pb['your_width']:.1f}% vs Ref {pb['reference_width']:.1f}% ({pb['difference']:+.1f}%)")

        # Suggestions Summary
        print(f"\n{'='*60}")
        print(f"SUGGESTIONS SUMMARY")
        print(f"{'='*60}\n")

        for summary_item in results['suggestions']['summary']:
            print(f"  • {summary_item}")

        # EQ Suggestions
        if results['suggestions']['eq_adjustments']:
            print(f"\nEQ ADJUSTMENTS ({len(results['suggestions']['eq_adjustments'])} total):")
            for i, eq in enumerate(results['suggestions']['eq_adjustments'][:5], 1):  # Show top 5
                print(f"  {i}. {eq['type'].upper():5s} {eq['frequency']:5d} Hz by {eq['gain_db']:+5.1f} dB (Q={eq['q']})")

        # Save full results to JSON
        output_file = Path(__file__).parent / "test_results.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"\nFull results saved to: {output_file}")

        print(f"\n{'='*60}")
        print(f"TEST COMPLETED SUCCESSFULLY!")
        print(f"{'='*60}\n")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_comparison()
