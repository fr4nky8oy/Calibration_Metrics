# A/B This - Reference Mix Comparison Tool

**Status:** Phase 1 (Backend MVP) Complete ✅

A web-based audio analysis tool that compares your mix against professional reference tracks, providing detailed frequency balance, masking, resonance, and dynamics analysis with actionable EQ suggestions.

---

## Project Overview

**A/B This** helps mixing engineers and producers improve their mixes by comparing them to professional reference tracks. Unlike existing plugin-based tools, A/B This is web-accessible and provides quantified differences with specific, actionable suggestions.

### Key Differentiators

- ✅ **Web-Based** - No plugin installation required
- ✅ **Quantitative Analysis** - Specific dB differences, not just visual
- ✅ **Actionable Suggestions** - Exact frequency/gain/Q EQ recommendations
- ✅ **Comprehensive Metrics** - 6-band frequency balance, masking, resonances, dynamics
- ✅ **Affordable** - Target: $5-10/month hosting (Railway hobby tier)

---

## Features Implemented (Phase 1 - Backend)

###  1. **6-Band Frequency Balance Analysis**
- Analyzes RMS levels across standard mixing bands:
  - Sub Bass (20-60Hz)
  - Bass (60-250Hz)
  - Low Mids (250-500Hz)
  - Mids (500Hz-2kHz)
  - High Mids (2-6kHz)
  - Highs (6-20kHz)
- Calculates energy percentage per band
- Generates specific EQ cut/boost suggestions

### 2. **Frequency Masking Detection**
- 11 critical band analysis (Bark scale)
- Detects overlapping frequency content
- Calculates clarity score (0-100)
- Identifies muddy/cluttered ranges
- Suggests separation techniques

### 3. **Resonance Detection**
- FFT-based peak finding
- Identifies harsh frequencies
- Calculates Q-factor for each resonance
- Classifies severity (high/moderate/low)
- Generates precise cut suggestions

### 4. **Dynamic Range Analysis**
- RMS and peak level measurement
- LUFS integrated loudness (ITU-R BS.1770)
- Crest factor calculation
- PLR (Peak to Loudness Ratio)
- Compression comparison
- Loudness matching suggestions

### 5. **FastAPI Backend**
- RESTful API with `/api/compare` endpoint
- File upload support (WAV, MP3, FLAC, M4A)
- Comprehensive JSON response
- CORS configured for frontend
- Railway deployment ready

---

## Project Structure

```
A_B_This/
├── backend/                    # Python FastAPI backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI app entry point
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── routes.py      # /api/compare endpoint
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py      # Settings
│   │   │   ├── spectrum_analyzer.py    # 6-band frequency balance
│   │   │   ├── masking_analyzer.py     # Critical band masking
│   │   │   ├── resonance_detector.py   # Peak finding
│   │   │   ├── dynamic_analyzer.py     # RMS/peak/LUFS
│   │   │   └── comparator.py           # Main orchestration
│   │   └── models/
│   │       ├── __init__.py
│   │       └── schemas.py     # Pydantic models
│   ├── requirements.txt
│   ├── railway.json           # Railway deployment config
│   ├── test_comparison.py     # Test script
│   └── README.md             # Backend docs
├── frontend/                   # React frontend (TODO: Phase 2)
└── README.md                  # This file
```

---

## Technology Stack

### Backend (✅ Complete)
- **Python 3.13**
- **FastAPI** - Modern async web framework
- **librosa 0.11.0** - Audio analysis and feature extraction
- **scipy 1.16.3** - Signal processing (FFT, filtering, peak detection)
- **pyloudnorm 0.1.1** - ITU-R BS.1770 LUFS measurement
- **numpy 2.3.4** - Array operations
- **soundfile 0.13.1** - Audio I/O
- **uvicorn** - ASGI server

### Frontend (TODO: Phase 2)
- **React 18** - UI framework
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Web Audio API** - Client-side playback and A/B switching
- **Chart.js** - Interactive spectrum visualization

### Deployment
- **Railway** ($7-10/month) - Backend hosting
- **Vercel** (Free) - Frontend hosting

---

## Quick Start (Backend)

### 1. Install Dependencies

```bash
cd A_B_This/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Run Test

```bash
python test_comparison.py
```

This will analyze two audio files and display:
- Processing time
- Frequency balance comparison
- Problem bands with EQ suggestions
- Masking analysis with clarity scores
- Resonance detection
- Dynamic range comparison
- Full suggestions summary

### 3. Run API Server

```bash
uvicorn app.main:app --reload --port 8000
```

API will be available at:
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/api/health
- **Compare Endpoint:** POST http://localhost:8000/api/compare

### 4. Test API Endpoint

```bash
curl -X POST "http://localhost:8000/api/compare" \
  -H "Content-Type: multipart/form-data" \
  -F "your_mix=@path/to/your_mix.wav" \
  -F "reference=@path/to/reference.wav"
```

---

## Test Results

**Example Output (test files):**

```
Processing Time: 0.5s

FREQUENCY BALANCE COMPARISON:
  sub_bass    :  +4.9 dB ⬆️
  bass        : +20.1 dB ⬆️
  low_mids    : +32.4 dB ⬆️
  mids        :  -6.9 dB ⬇️
  high_mids   :  -6.8 dB ⬇️
  highs       : +12.2 dB ⬆️

MASKING ANALYSIS:
  Your Mix Clarity:  63/100
  Reference Clarity: 52/100
  Difference:        +11

RESONANCE COMPARISON:
  Your Mix High Severity:  0
  Reference High Severity: 1

EQ ADJUSTMENTS (7 total):
  1. CUT      40 Hz by  -3.4 dB (Q=1.0)
  2. CUT     120 Hz by -14.1 dB (Q=1.0)
  3. CUT     350 Hz by -22.7 dB (Q=1.0)
  4. BOOST  1000 Hz by  +4.8 dB (Q=1.0)
  5. BOOST  3500 Hz by  +4.8 dB (Q=1.0)
```

---

## API Response Example

```json
{
  "success": true,
  "processing_time": 22.5,
  "your_mix": {
    "filename": "my_mix.wav",
    "duration": 225,
    "frequency_balance": {
      "sub_bass": {"level_db": -24.2, "energy_percent": 8.5},
      "bass": {"level_db": -18.7, "energy_percent": 22.3},
      ...
    },
    "masking": {
      "clarity_score": 68,
      "issues": [...]
    },
    "resonances": [...],
    "dynamics": {
      "rms_db": -18.2,
      "peak_db": -2.1,
      "lufs_integrated": -14.2,
      "crest_factor": 16.1,
      "plr": 8.5
    },
    "spectrum_data": {
      "frequencies": [20, 25, 31, ...],
      "magnitudes": [-45, -42, -38, ...]
    }
  },
  "reference": {...},
  "comparison": {...},
  "suggestions": {
    "eq_adjustments": [
      {"type": "cut", "frequency": 280, "gain_db": -3.2, "q": 1.8},
      ...
    ],
    "compression": {...},
    "masking": [...],
    "summary": ["Major frequency imbalance in: bass, low mids"]
  }
}
```

---

## Performance

- **Processing Time:** 20-30 seconds for typical 3-5 minute tracks
- **Optimization:** Audio downsampled to 22kHz (50% speed boost with minimal quality impact for analysis)
- **Target:** Sub-30s for Railway hobby tier

---

## Development Roadmap

### ✅ Phase 1: Backend MVP (COMPLETE - 2 weeks)
- [x] Project structure and dependencies
- [x] 6-band frequency balance analysis
- [x] Frequency masking detection
- [x] Resonance detection with Q-factor
- [x] Dynamic range and LUFS analysis
- [x] FastAPI endpoint with file upload
- [x] Testing with sample files
- [x] Railway deployment configuration

### 🚧 Phase 2: Frontend MVP (Next - 3-4 weeks)
- [ ] React project setup with Vite
- [ ] Dual file upload component
- [ ] Web Audio API A/B playback
- [ ] Interactive spectrum graph overlay
- [ ] Frequency band comparison display
- [ ] Masking visualization heatmap
- [ ] Resonance table with suggestions
- [ ] Dynamic range comparison cards
- [ ] Export PDF report
- [ ] Deploy to Vercel

### 📅 Phase 3: Polish & Features (4-5 weeks)
- [ ] Real-time EQ preview (Web Audio API)
- [ ] Solo frequency bands
- [ ] Export EQ presets (FabFilter Pro-Q3 format)
- [ ] Mobile-responsive design
- [ ] User authentication
- [ ] Save/load comparison history
- [ ] Public reference library

### 📅 Phase 4: Advanced Features (Future)
- [ ] Stereo width per band
- [ ] Phase correlation analysis
- [ ] Time-based comparison (verse vs verse)
- [ ] Multi-track comparison (3+ files)
- [ ] AI-powered genre detection
- [ ] Collaborative features

---

## Competitive Analysis

| Tool | Platform | Price | A/B This Advantage |
|------|----------|-------|-------------------|
| iZotope Tonal Balance Control | Plugin | $129+ | Web-based, detailed metrics, specific suggestions |
| REFERENCE by Mastering The Mix | Plugin | $99 | Web-based, downloadable reports, cheaper |
| LEVELS | Plugin | $99 | Frequency comparison + masking analysis |
| Metric AB | Plugin | Free | Quantitative analysis, not just switching |
| SPAN | Plugin | Free | Automated comparison, actionable suggestions |

---

## Cost Breakdown

### Monthly Operating Costs
| Service | Cost | Purpose |
|---------|------|---------|
| Railway (Backend) | $7-10 | Python FastAPI analysis API |
| Vercel (Frontend) | FREE | React app hosting |
| **Total** | **$7-10/month** | |

### Monetization Strategy (Future)

**Free Tier:**
- 5 comparisons per month
- Basic frequency balance + dynamics
- Standard report

**Pro Tier ($9.99/month):**
- Unlimited comparisons
- All analysis features
- Advanced visualizations
- EQ preset downloads
- PDF reports
- No ads

**Studio Tier ($29.99/month):**
- Everything in Pro
- Team collaboration
- Historical tracking
- API access
- White-label reports

---

## Next Steps

1. **Deploy Backend to Railway**
   ```bash
   railway login
   railway init
   railway up
   ```

2. **Start Frontend Development**
   - Set up React + Vite + Tailwind
   - Build dual file upload
   - Integrate Web Audio API
   - Create spectrum visualization

3. **Integration Testing**
   - Connect frontend to deployed backend
   - Test with real audio files
   - Performance optimization

4. **Beta Launch**
   - Reddit: r/audioengineering, r/mixingmastering
   - Collect feedback
   - Iterate on UX

---

## Contributing

This project is currently in MVP development. Contributions welcome after Phase 2 completion.

---

## License

MIT License - See LICENSE file for details

---

## Contact

For questions or feedback, please open an issue on GitHub.

---

**Created:** November 10, 2025
**Status:** Phase 1 Complete (Backend MVP)
**Next Milestone:** Phase 2 - React Frontend with Web Audio API

