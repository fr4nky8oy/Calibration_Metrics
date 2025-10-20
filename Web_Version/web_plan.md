# ACX Audio Analyzer - Web Version Plan

## Project Overview
Build a professional web application for ACX audiobook compliance checking and audio analysis. This will be a free, open-source alternative to paid ACX checker apps, deployable on the web with full Python analysis quality.

## Tech Stack

### Backend
- **Framework:** FastAPI (Python 3.13)
- **Audio Processing:**
  - librosa (audio analysis)
  - soundfile (audio I/O)
  - pyloudnorm (LUFS measurements)
  - numpy (array operations)
- **Server:** Uvicorn (ASGI server)
- **Hosting:** Render.com (FREE tier or $7/month paid)

### Frontend
- **Framework:** React 18+
- **Styling:** Tailwind CSS
- **Build Tool:** Vite
- **File Upload:** react-dropzone
- **HTTP Client:** axios
- **Hosting:** Vercel or Netlify (FREE)

### Deployment
- **Backend:** Render.com (auto-deploy from GitHub)
- **Frontend:** Vercel (auto-deploy from GitHub)
- **Domain:** Use existing Fasthost domain (optional)

## Architecture

```
┌─────────────────────────────────────────┐
│  Frontend (React + Tailwind)           │
│  Hosted on: Vercel/Netlify (FREE)      │
├─────────────────────────────────────────┤
│  • File drag-and-drop interface        │
│  • Upload to backend API                │
│  • Display results (color-coded)        │
│  • Export report (text/PDF)             │
│  • Responsive design (mobile-friendly)  │
└─────────────────────────────────────────┘
                  ↓ HTTP/HTTPS
                  ↓ (REST API)
┌─────────────────────────────────────────┐
│  Backend (FastAPI + Python)             │
│  Hosted on: Render.com (FREE/paid)      │
├─────────────────────────────────────────┤
│  Endpoints:                             │
│  • POST /api/analyze - Upload & analyze │
│  • GET /api/health - Health check       │
│  • GET /api/formats - Supported formats │
│                                         │
│  Processing:                            │
│  • Receive audio file                   │
│  • Run existing analyzer code           │
│  • Return JSON results                  │
│  • Immediate file deletion (privacy)    │
└─────────────────────────────────────────┘
```

## Project Structure

```
CalibrationMetrics/
├── Web_Version/
│   ├── backend/                    # FastAPI backend
│   │   ├── app/
│   │   │   ├── __init__.py
│   │   │   ├── main.py            # FastAPI app
│   │   │   ├── api/
│   │   │   │   ├── __init__.py
│   │   │   │   └── routes.py      # API endpoints
│   │   │   ├── core/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── config.py      # Settings
│   │   │   │   └── analyzer.py    # Audio analysis logic
│   │   │   └── models/
│   │   │       ├── __init__.py
│   │   │       └── schemas.py     # Pydantic models
│   │   ├── requirements.txt
│   │   ├── Dockerfile             # For Render deployment (optional)
│   │   └── README.md
│   │
│   ├── frontend/                   # React frontend
│   │   ├── public/
│   │   │   └── index.html
│   │   ├── src/
│   │   │   ├── App.jsx            # Main component
│   │   │   ├── main.jsx           # Entry point
│   │   │   ├── components/
│   │   │   │   ├── FileUpload.jsx
│   │   │   │   ├── Results.jsx
│   │   │   │   ├── Header.jsx
│   │   │   │   └── Footer.jsx
│   │   │   ├── services/
│   │   │   │   └── api.js         # API client
│   │   │   └── styles/
│   │   │       └── index.css      # Tailwind imports
│   │   ├── package.json
│   │   ├── vite.config.js
│   │   ├── tailwind.config.js
│   │   └── README.md
│   │
│   └── web_plan.md                 # This file
```

## Development Phases

### Phase 1: Backend API (6-8 hours)

**Tasks:**
1. Set up FastAPI project structure
2. Convert existing `audio_analyzer.py` to modular API
3. Create `/api/analyze` endpoint (accepts file upload)
4. Implement audio analysis (reuse existing code)
5. Return JSON response with results
6. Add error handling and validation
7. Test with Postman/curl
8. Add CORS middleware (for frontend access)

**Output:**
- Working API at `http://localhost:8000`
- Endpoint: `POST /api/analyze` accepts audio files
- Returns JSON with ACX compliance results

**Testing:**
```bash
curl -X POST http://localhost:8000/api/analyze \
  -F "file=@test_audio.wav"
```

---

### Phase 2: Frontend UI (4-5 hours)

**Tasks:**
1. Set up React + Vite project
2. Install Tailwind CSS
3. Create components:
   - FileUpload (drag-and-drop)
   - Results (display analysis)
   - Header (title, description)
   - Footer (credits, GitHub link)
4. Style with Tailwind (modern, clean design)
5. Connect to backend API
6. Add loading states and error handling
7. Test locally

**Design Features:**
- Clean, modern interface (like Stripe/Vercel)
- Drag-and-drop file upload zone
- Color-coded results (✅ green, ❌ red, ⚠️ yellow)
- Smooth animations
- Responsive (mobile-friendly)
- Export report button

**Output:**
- Working frontend at `http://localhost:5173`
- Connects to backend API
- Beautiful, professional UI

---

### Phase 3: Integration & Testing (2-3 hours)

**Tasks:**
1. Connect frontend to backend API
2. Test full workflow (upload → analyze → results)
3. Test with various audio files
4. Test error cases (wrong format, too large, etc.)
5. Add loading indicators
6. Polish UI/UX
7. Add export report feature

**Test cases:**
- WAV files (various sizes)
- MP3 files
- Large files (3+ hours)
- Invalid files (should show error)
- Network errors (should handle gracefully)

---

### Phase 4: Deployment (2-3 hours)

**Backend (Render.com):**
1. Create Render account (already done ✅)
2. Connect GitHub repository (already done ✅)
3. Create new Web Service
4. Configure environment variables
5. Deploy backend
6. Get API URL: `https://your-app.onrender.com`

**Frontend (Vercel):**
1. Create Vercel account (already done ✅)
2. Connect GitHub repository (already done ✅)
3. Configure API URL environment variable
4. Deploy frontend
5. Get frontend URL: `https://your-app.vercel.app`

**Optional:**
- Point custom domain to Vercel frontend
- Example: `audioanalyzer.yourdomain.com`

---

### Phase 5: Polish & Launch (2-3 hours)

**Tasks:**
1. Add landing page content
2. Write privacy policy (files deleted immediately)
3. Add "About" section
4. Link to GitHub repository
5. Add analytics (optional)
6. Test on mobile devices
7. Final polish

**Launch:**
- Post on Reddit (r/audioengineering, r/audiobook)
- Share on Twitter/X
- ACX/Audible forums
- Add to your portfolio

---

## API Specification

### POST /api/analyze

**Request:**
```http
POST /api/analyze HTTP/1.1
Content-Type: multipart/form-data

file: <audio_file>
```

**Response (Success):**
```json
{
  "success": true,
  "file_info": {
    "filename": "my_audio.wav",
    "duration": "2:45",
    "format": "WAV",
    "sample_rate": 96000,
    "channels": 1,
    "bitrate": "1536 kbps"
  },
  "acx_compliance": {
    "overall_pass": false,
    "checks": {
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
    }
  },
  "additional_metrics": {
    "lufs": -16.2,
    "true_peak": -2.8,
    "reverb_level": "low"
  },
  "elevenlabs": {
    "length_ok": false,
    "quality_ok": true
  }
}
```

**Response (Error):**
```json
{
  "success": false,
  "error": "Invalid file format. Supported: WAV, MP3, M4A, FLAC"
}
```

---

## Privacy & Security

**File Handling:**
- Files processed in memory (never written to disk)
- Immediate deletion after analysis
- No logging of file contents
- SSL encryption for uploads (HTTPS)

**Privacy Policy:**
- Clear statement on landing page
- "Your files are never stored"
- "Processing happens in memory"
- "Files deleted immediately after analysis"

**Open Source:**
- All code on GitHub (transparency)
- Users can verify no file storage
- Option to self-host (provide Docker image)

---

## Cost Breakdown

### Monthly Costs

| Service | Cost | Purpose |
|---------|------|---------|
| Render.com (Backend) | FREE or $7 | Host Python API |
| Vercel (Frontend) | FREE | Host React app |
| Domain (optional) | ~$1/month | Custom URL |
| **Total** | **$0 or $7/month** | |

### Scaling Costs

| Users/Month | Render Cost | Notes |
|-------------|-------------|-------|
| 0-100 | FREE | Free tier (with cold starts) |
| 100-500 | $7 | Starter plan (always-on) |
| 500-2000 | $7-25 | May need Pro plan |
| 2000+ | $25+ | Pro plan or optimize |

---

## Future Features (Post-Launch)

### Phase 6: AI Denoiser
- Add `/api/denoise` endpoint
- Upload noisy audio → return cleaned audio
- Use AI model (needs GPU server, ~$20-50/month)
- Before/after comparison UI

### Phase 7: Advanced Features
- User accounts (save analysis history)
- Batch processing (multiple files)
- Audio normalization (auto-fix RMS)
- Room tone injection
- MP3 conversion with correct settings
- Share results via URL

### Phase 8: Monetization (Optional)
- Free tier: Basic ACX checking
- Pro tier: AI denoiser, batch processing, priority support
- API access for other apps

---

## Timeline

**Total Development Time: 16-22 hours**

| Phase | Hours | Calendar Time |
|-------|-------|---------------|
| Phase 1: Backend API | 6-8 hours | Week 1 |
| Phase 2: Frontend UI | 4-5 hours | Week 2 |
| Phase 3: Integration | 2-3 hours | Week 2 |
| Phase 4: Deployment | 2-3 hours | Week 3 |
| Phase 5: Polish | 2-3 hours | Week 3 |

**Target Launch: 3 weeks from start**

---

## Success Metrics

**Technical:**
- API response time < 60 seconds for 1-hour audio
- 99% uptime
- No file storage (verify with logs)
- Mobile-responsive (works on all devices)

**User Growth:**
- 100 users in first month
- 500 users in 3 months
- 1000+ users in 6 months
- GitHub stars: 50+ in first 3 months

**Community:**
- Featured on ACX forums
- Reddit upvotes
- User testimonials
- Contributors to open source

---

## Tech Decisions & Rationale

### Why FastAPI?
- Modern Python web framework
- Fast performance (async)
- Automatic API documentation (Swagger)
- Easy to learn
- Type hints (better code quality)

### Why React?
- Industry standard
- Great for SPAs
- Large ecosystem
- Reusable components
- Easy to add features later (AI denoiser UI)

### Why Tailwind CSS?
- Modern, utility-first
- Fast development
- Beautiful by default
- Responsive helpers
- Small bundle size

### Why Render.com?
- Easy Python deployment
- Auto-deploy from GitHub
- Generous FREE tier for testing
- Simple upgrade to $7/month (always-on)
- Great developer experience
- No confusing credit system

### Why Vercel?
- Best free hosting for React
- Auto-deploy from GitHub
- Global CDN
- Built-in SSL
- Perfect for static sites

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Large files crash server | Limit file size (100MB max) |
| Slow analysis (60+ sec) | Add progress updates via WebSocket |
| Privacy concerns | Clear policy, open source, no storage |
| Costs scale too high | Monitor usage, optimize code, add rate limiting |
| Low user adoption | Market to ACX community, Reddit, forums |
| Server downtime | Use Railway's monitoring, set up alerts |

---

## Next Steps

1. **Review this plan** - Make sure everything aligns with vision
2. **Set up development environment** - Install tools
3. **Start Phase 1** - Build FastAPI backend
4. **Test locally** - Verify analysis works
5. **Move to Phase 2** - Build React frontend
6. **Deploy** - Launch on Railway + Vercel
7. **Promote** - Share with ACX community

---

## Resources & Links

**Documentation:**
- FastAPI: https://fastapi.tiangolo.com/
- React: https://react.dev/
- Tailwind CSS: https://tailwindcss.com/
- Vite: https://vitejs.dev/
- Render: https://render.com/
- Vercel: https://vercel.com/

**Inspiration (Design):**
- https://vercel.com (clean, modern)
- https://stripe.com (professional, minimal)
- https://linear.app (beautiful UI)

**Community:**
- Reddit: r/audioengineering, r/audiobook, r/ACX
- GitHub: Tag with #acx #audiobook #audio-analysis

---

## Notes

- This plan prioritizes **quality** (full Python stack) over shortcuts (Web Audio API)
- Architecture is **future-proof** (ready for AI denoiser and other features)
- Approach is **professional** (production-ready, scalable)
- Design will be **modern and polished** (React + Tailwind)
- Privacy is **transparent** (open source, clear policy)

---

**Last Updated:** October 20, 2025
**Status:** Planning Phase → Starting Phase 1
**Next Action:** Build FastAPI backend (Phase 1)
**Hosting Decision:** ✅ Render.com (FREE tier) + Vercel (FREE)
