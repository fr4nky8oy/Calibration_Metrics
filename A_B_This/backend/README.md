# A/B This - Backend API

Reference mix comparison tool backend built with FastAPI and Python audio analysis libraries.

## Features

- **6-Band Frequency Balance** - Compare RMS levels across standard mixing bands
- **Frequency Masking Detection** - Identify cluttered frequency ranges
- **Resonance Detection** - Find harsh peaks and resonances
- **Dynamic Range Analysis** - Compare RMS, peak, LUFS, compression
- **Actionable EQ Suggestions** - Get specific frequency/gain/Q recommendations

## Installation

### 1. Create Virtual Environment

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your settings
```

## Running Locally

```bash
# Development mode (with auto-reload)
uvicorn app.main:app --reload --port 8000

# Or using Python directly
python -m app.main
```

API will be available at:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/api/health

## API Endpoints

### POST /api/compare

Compare two audio files.

**Request:**
- Content-Type: multipart/form-data
- your_mix: Audio file (WAV, MP3, FLAC, M4A)
- reference: Audio file (WAV, MP3, FLAC, M4A)

**Response:**
```json
{
  "success": true,
  "processing_time": 22.5,
  "your_mix": {
    "filename": "my_mix.wav",
    "frequency_balance": { ... },
    "masking": { ... },
    "resonances": [ ... ],
    "dynamics": { ... },
    "spectrum_data": { ... }
  },
  "reference": { ... },
  "comparison": { ... },
  "suggestions": {
    "eq_adjustments": [ ... ],
    "compression": { ... },
    "masking": [ ... ],
    "summary": [ ... ]
  }
}
```

### GET /api/health

Health check endpoint.

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py              # API endpoints
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py              # Settings
│   │   ├── spectrum_analyzer.py   # Frequency balance
│   │   ├── masking_analyzer.py    # Masking detection
│   │   ├── resonance_detector.py  # Peak finding
│   │   ├── dynamic_analyzer.py    # RMS/peak/LUFS
│   │   └── comparator.py          # Main comparison logic
│   └── models/
│       ├── __init__.py
│       └── schemas.py             # Pydantic models
├── requirements.txt
├── railway.json
├── .env.example
├── .gitignore
└── README.md
```

## Analysis Modules

### spectrum_analyzer.py
- 6-band frequency analysis (20Hz-20kHz)
- Butterworth bandpass filtering
- RMS level calculation per band
- Energy percentage distribution
- EQ suggestion generation

### masking_analyzer.py
- 11 critical band analysis (Bark scale)
- Spectral flatness calculation
- Adjacent band overlap detection
- Clarity score (0-100)
- Masking issue identification

### resonance_detector.py
- FFT-based peak detection
- Prominence and Q-factor estimation
- Severity classification
- Frequency-specific cut suggestions
- Harsh range identification

### dynamic_analyzer.py
- RMS and peak level measurement
- LUFS integrated loudness (ITU-R BS.1770)
- Crest factor calculation
- PLR (Peak to Loudness Ratio)
- Compression analysis

## Deployment (Railway)

1. Install Railway CLI:
```bash
npm install -g @railway/cli
```

2. Login and initialize:
```bash
railway login
railway init
```

3. Deploy:
```bash
railway up
```

4. Set environment variables in Railway dashboard

## Development

### Running Tests
```bash
# TODO: Add tests
pytest
```

### Code Style
```bash
# Format with black
black app/

# Lint with flake8
flake8 app/
```

## Performance Optimization

- Audio downsampled to 22kHz (50% speed boost)
- Welch's method for smooth spectrum
- Efficient scipy filtering
- Target processing time: 20-30 seconds per comparison

## Troubleshooting

### libsndfile Error
If you get errors about libsndfile:
```bash
# macOS
brew install libsndfile

# Ubuntu/Debian
sudo apt-get install libsndfile1

# Windows
# Included in soundfile pip package
```

### Memory Issues
For large files, reduce downsample_sr in config.py or set max_file_size_mb lower.

## License

MIT License - See LICENSE file for details

## Support

For issues or questions, please open an issue on GitHub.
