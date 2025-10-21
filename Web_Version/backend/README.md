# ACX Audio Analyzer API - Backend

FastAPI backend for ACX audiobook compliance checking and audio analysis.

## Features

- ✅ **ACX Compliance Checking** - RMS, peak, noise floor, format, duration, room tone
- ✅ **ElevenLabs Guidelines** - Voice cloning quality validation
- ✅ **Additional Metrics** - LUFS, true peak, reverb estimation
- ✅ **RESTful API** - Clean JSON responses
- ✅ **CORS Enabled** - Works with any frontend
- ✅ **Privacy-First** - Files processed in memory, immediately deleted
- ✅ **Auto Documentation** - Swagger/OpenAPI docs at `/docs`

## Tech Stack

- **Framework:** FastAPI 0.104.1
- **Server:** Uvicorn
- **Audio Processing:** librosa, soundfile, pyloudnorm
- **Python:** 3.13+

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app + endpoints
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py        # Settings
│   │   └── analyzer.py      # Audio analysis logic
│   └── models/
│       ├── __init__.py
│       └── schemas.py       # Pydantic models
├── requirements.txt
└── README.md (this file)
```

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

### 3. Install FFmpeg (Required)

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Windows:**
Download from https://ffmpeg.org/download.html

## Running the API

### Development Mode

```bash
# From backend/ directory
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at:
- **API:** http://localhost:8000
- **Swagger Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## API Endpoints

### `GET /`
Root endpoint - API information

### `GET /api/health`
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "message": "API is running and ready to analyze audio files"
}
```

### `GET /api/formats`
Get supported audio formats and file size limits

**Response:**
```json
{
  "supported_formats": ["WAV", "MP3", "FLAC", "M4A"],
  "max_file_size_mb": 100
}
```

### `POST /api/analyze`
Analyze audio file for ACX and ElevenLabs compliance

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: `file` (audio file)

**Example with curl:**
```bash
curl -X POST http://localhost:8000/api/analyze \
  -F "file=@/path/to/audio.wav"
```

**Response (Success):**
```json
{
  "success": true,
  "file_info": {
    "filename": "audio.wav",
    "duration": "2:45",
    "duration_seconds": 165.0,
    "format": "WAV",
    "sample_rate": 96000,
    "channels": 1,
    "bitrate": "1536 kbps"
  },
  "acx_compliance": {
    "overall_pass": false,
    "rms": {
      "value": -21.3,
      "pass": true,
      "range": "-23 to -18 dB"
    },
    "peak": {
      "value": -4.2,
      "pass": true,
      "threshold": "< -3 dB"
    },
    "noise_floor": {
      "value": -68.5,
      "pass": true,
      "threshold": "< -60 dB"
    },
    "format": {
      "value": "WAV (PCM_F32LE, 96kHz)",
      "pass": false,
      "required": "MP3 192+ kbps CBR, 44.1kHz"
    },
    "duration": {
      "value": 165,
      "pass": true,
      "max": 7200
    },
    "room_tone": {
      "detected": false,
      "pass": false,
      "required": "1-5 seconds at start/end"
    }
  },
  "additional_metrics": {
    "lufs": -16.2,
    "true_peak": -2.8,
    "reverb_level": "low"
  },
  "elevenlabs": {
    "length_ok": true,
    "quality_ok": true,
    "length_minutes": 2.75,
    "length_requirement": "Minimum 1 minute (30+ recommended)",
    "quality_requirement": "Clean audio with minimal background noise"
  }
}
```

**Response (Error):**
```json
{
  "success": false,
  "error": "Invalid file format. Supported formats: .wav, .mp3, .flac, .m4a",
  "detail": null
}
```

## Testing the API

### Using curl

```bash
# Health check
curl http://localhost:8000/api/health

# Get supported formats
curl http://localhost:8000/api/formats

# Analyze audio file
curl -X POST http://localhost:8000/api/analyze \
  -F "file=@test_audio.wav"
```

### Using Python requests

```python
import requests

url = "http://localhost:8000/api/analyze"
files = {"file": open("test_audio.wav", "rb")}
response = requests.post(url, files=files)
print(response.json())
```

### Using the Swagger UI

1. Start the server
2. Open http://localhost:8000/docs
3. Click "Try it out" on `/api/analyze`
4. Upload a file and click "Execute"

## Configuration

### CORS Configuration

CORS is configured in `app/main.py` using regex patterns:

```python
# Current configuration (updated Oct 21, 2025)
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https://.*\.vercel\.app|https://.*\.netlify\.app|https://analisethis\.frankyredente\.com|http://localhost:\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

To add your custom domain, update the regex pattern in `app/main.py` line 33.

### Other Settings

Edit `app/core/config.py` to change settings:

```python
# Max file size (default: 100MB)
MAX_FILE_SIZE = 100 * 1024 * 1024

# Allowed formats
ALLOWED_EXTENSIONS = [".wav", ".mp3", ".flac", ".m4a"]
```

## Deployment to Railway

**Note:** This project is currently deployed on Railway (not Render) due to better memory allocation for audio processing.

### 1. Create New Project

1. Go to https://railway.app
2. Click "New Project" → "Deploy from GitHub repo"
3. Connect your GitHub account and select repository
4. Railway will auto-detect the project

### 2. Configuration Files

The deployment is configured via these files (already set up):

**`railway.json`** - Deployment settings:
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS",
    "nixpacksConfigPath": "nixpacks.toml"
  },
  "deploy": {
    "startCommand": "/opt/venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT"
  }
}
```

**`nixpacks.toml`** - Build configuration (simplified Oct 21, 2025):
```toml
[phases.setup]
aptPkgs = ["ffmpeg"]

[phases.install]
cmds = [
  "python3 -m venv /opt/venv",
  "/opt/venv/bin/pip install --upgrade pip",
  "/opt/venv/bin/pip install -r requirements.txt"
]

[start]
cmd = "/opt/venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT"
```

### 3. Environment Variables

No environment variables required for basic setup.

### 4. Deploy

1. Push changes to GitHub
2. Railway auto-deploys from the main branch
3. Build takes ~8-10 minutes
4. Your API will be available at: `https://your-project.up.railway.app`

### 5. Railway Settings

- **Memory:** 8GB RAM (required for audio processing)
- **Cost:** ~$5-10/month
- **Auto-deploy:** Enabled from GitHub main branch

### Deployment Troubleshooting

**Build timeout:**
- Ensure `nixpacks.toml` is simplified (see above)
- Remove redundant `Procfile` and `Aptfile` if present

**CORS errors:**
- Add your custom domain to `app/main.py` CORS middleware (line 33)

## Troubleshooting

### FFmpeg not found

**Error:** `ffprobe: command not found`

**Solution:** Install FFmpeg:
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg
```

### Import errors

**Error:** `ModuleNotFoundError: No module named 'app'`

**Solution:** Make sure you're running from the `backend/` directory:
```bash
cd backend
uvicorn app.main:app --reload
```

### CORS errors

**Error:** Frontend can't connect due to CORS

**Solution:** Add your frontend URL to `CORS_ORIGINS` in `app/core/config.py`

## Development

### Adding new endpoints

1. Add route to `app/main.py`
2. Create Pydantic models in `app/models/schemas.py` (if needed)
3. Test with `/docs` or curl

### Modifying analysis logic

Edit `app/core/analyzer.py` - all analysis functions are here.

## License

MIT License - Free to use for personal and commercial projects

## Support

- **Issues:** https://github.com/your-username/acx-audio-analyzer/issues
- **Docs:** http://localhost:8000/docs (when running)
