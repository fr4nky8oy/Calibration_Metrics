# Speed Improvement Strategies for AnaliseThis

## Current Performance Issues

**Current Analysis Time:** ~30-90 seconds per minute of audio

### Identified Bottlenecks

1. **File Upload Time** - Audio files (especially WAV) can be 10-100MB+ and need to upload to Railway server
2. **Python librosa** - Powerful but slow, processes entire audio file in Python (interpreted, not compiled)
3. **Sequential Processing** - All metrics calculated one after another, not in parallel
4. **Full File Analysis** - Analyzes every sample from start to finish
5. **Server Location** - Railway server might be geographically distant from users

---

## Why VST Plugins Are Faster (10-20 seconds)

VST audio plugins can analyze audio much faster because:

- **Local Processing** - No upload needed, direct audio buffer access
- **Compiled Code** - Written in C/C++, 10-100x faster than Python
- **Real-Time Optimized** - Built for live audio processing
- **Simpler Algorithms** - Often use faster approximations
- **Hardware Access** - Can use CPU SIMD instructions, sometimes GPU acceleration

---

## Speed Improvement Options

### 1. Quick Wins (Minimal Changes) ⚡

**Easy to implement, immediate results**

- **Downsample for analysis** - Analyze at 22.05kHz instead of 96kHz (4x faster, still accurate for ACX/ElevenLabs checks)
- **Parallel processing** - Use Python multiprocessing for independent metrics (RMS, peak, noise floor can run simultaneously)
- **Skip heavy calculations** - Reverb estimation is slowest, make it optional or use faster approximation
- **Optimize room tone detection** - Only analyze first/last 10 seconds instead of whole file
- **Add progress indicators** - Show real-time progress (doesn't speed up, but feels faster)

**Expected Improvement:** 60s → 15-25s per minute of audio (2-4x faster)

**Implementation Effort:** Low (few hours)

**Code Changes:**
- Modify `backend/app/core/analyzer.py`
- Add `multiprocessing` for parallel metric calculation
- Add downsampling step before analysis
- Limit room tone scan to edges only

---

### 2. Use Faster Tools (Moderate Effort) 🔧

**Replace slow libraries with optimized alternatives**

- **FFmpeg for everything** - FFmpeg is C-based, much faster than librosa for basic metrics (RMS, peak, duration)
- **pydub instead of librosa** - Lighter library for simpler operations, built on FFmpeg
- **Sonic Visualiser libraries** - C++ libraries with Python bindings
- **aubio** - Fast C library for audio analysis with Python bindings
- **Essentia** - Optimized for music/audio analysis, used by Spotify

**Expected Improvement:** 10-15s per minute of audio (4-6x faster)

**Implementation Effort:** Moderate (1-2 days)

**Code Changes:**
- Replace librosa calls with FFmpeg subprocess commands
- Use pydub for loading/basic analysis
- Keep librosa only for LUFS (uses pyloudnorm)

---

### 3. Browser-Based Processing (Significant Rewrite) 🌐

**Process audio entirely in user's browser**

- **Web Audio API** - Process audio entirely in browser (JavaScript)
- **WebAssembly (WASM)** - Compile C/C++ audio analysis code to run in browser at near-native speed
- **No server needed** - Instant analysis, no upload time, zero server costs
- **Offline capability** - Works without internet after first load

**Expected Improvement:** 5-15 seconds total for any file (10-15x faster)

**Implementation Effort:** High (1-2 weeks)

**Pros:**
- Fastest possible experience
- No server costs for analysis
- Works offline
- Privacy - files never leave user's device

**Cons:**
- Browser memory limits (may struggle with >500MB files)
- Less powerful than Python libraries
- Cross-browser compatibility issues
- Requires JavaScript/C++ expertise

**Architecture:**
```
Frontend (React + Web Audio API + WASM)
├── Load audio file into AudioBuffer
├── Extract audio data (samples)
├── Calculate metrics in browser:
│   ├── RMS (JavaScript or WASM)
│   ├── Peak (JavaScript or WASM)
│   ├── Noise floor (WASM)
│   ├── LUFS (WASM - port pyloudnorm)
│   └── Format detection (File API)
└── Display results (no backend needed)
```

---

### 4. Better Infrastructure 💰

**Upgrade server/architecture**

- **Faster CPU server** - Railway's current tier may have limited CPU cores/speed
- **More RAM** - Allow larger files to be processed in memory
- **Edge computing** - Cloudflare Workers or AWS Lambda@Edge, closer to users geographically
- **GPU acceleration** - Limited benefit for audio, but some operations (FFT) can use GPU
- **CDN for uploads** - Use S3 + CloudFront for faster regional uploads
- **Caching** - Cache results for identical files (hash-based)

**Expected Improvement:** 20-40% faster (1.2-1.5x)

**Implementation Effort:** Low to Moderate (configuration changes mostly)

**Cost Impact:** $20-50/month additional

---

### 5. Sampling Strategy (Trade Accuracy for Speed) 🎲

**Analyze representative portions instead of entire file**

- **Analyze random 30-second chunks** - Most metrics stable after analyzing small portion
- **Statistical estimation** - RMS/peak stable after analyzing 10% of file
- **Progressive analysis** - Show quick results immediately, then refine in background
- **Smart sampling** - Analyze beginning, middle, end, and random sections

**Expected Improvement:** 5-10 seconds for any file length (10-20x faster)

**Implementation Effort:** Moderate (few days)

**Trade-offs:**
- Slightly less accurate (±1-2 dB potential variance)
- May miss transient issues
- Room tone detection still requires full file scan
- Not suitable for files with highly variable content

---

## Recommended Implementation Path

### Phase 1: Quick Wins (This Month)
1. ✅ Downsample to 22.05kHz for analysis
2. ✅ Parallelize independent metrics
3. ✅ Skip reverb estimation (or make optional)
4. ✅ Optimize room tone detection to 10-second scans
5. ✅ Add real-time progress updates

**Target:** Reduce from 60s to 15-25s per minute of audio

---

### Phase 2: Tool Optimization (Next Month)
1. ✅ Replace librosa with FFmpeg for basic metrics
2. ✅ Use pydub for file loading
3. ✅ Keep Python only for LUFS and complex analysis
4. ✅ Add caching for repeated analyses

**Target:** Reduce to 10-15s per minute of audio

---

### Phase 3: Browser Processing (Future/V2.0)
1. ✅ Research Web Audio API + WASM approach
2. ✅ Build proof-of-concept for basic metrics
3. ✅ Port critical algorithms to WASM
4. ✅ Keep backend as optional "deep analysis" mode
5. ✅ Hybrid: Quick browser scan + optional detailed server analysis

**Target:** 5-10s total for most users, instant for simple checks

---

## Comparison: Different Approaches

| Approach | Speed | Accuracy | Effort | Cost | Privacy |
|----------|-------|----------|--------|------|---------|
| Current | ⭐ | ⭐⭐⭐⭐⭐ | - | $10/mo | ⭐⭐⭐ |
| Quick Wins | ⭐⭐⭐ | ⭐⭐⭐⭐ | Low | $10/mo | ⭐⭐⭐ |
| Faster Tools | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Moderate | $10/mo | ⭐⭐⭐ |
| Browser-Based | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | High | $0 | ⭐⭐⭐⭐⭐ |
| Better Infrastructure | ⭐⭐ | ⭐⭐⭐⭐⭐ | Low | $30-50/mo | ⭐⭐⭐ |
| Sampling | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | Moderate | $10/mo | ⭐⭐⭐ |

---

## Technical Details: Quick Wins Implementation

### 1. Downsampling
```python
# Before (slow)
y, sr = librosa.load(audio_path)  # Loads at original 96kHz

# After (fast)
y, sr = librosa.load(audio_path, sr=22050)  # Resample to 22.05kHz
# 96kHz → 22.05kHz = 4.3x fewer samples = 4x faster
```

### 2. Parallel Processing
```python
import concurrent.futures

def analyze_parallel(audio_path):
    with concurrent.futures.ProcessPoolExecutor() as executor:
        rms_future = executor.submit(calculate_rms, audio_path)
        peak_future = executor.submit(calculate_peak, audio_path)
        noise_future = executor.submit(calculate_noise, audio_path)

        return {
            'rms': rms_future.result(),
            'peak': peak_future.result(),
            'noise': noise_future.result()
        }
```

### 3. Skip/Optimize Reverb
```python
# Option 1: Skip entirely (fastest)
reverb_level = "unknown"  # Or remove from results

# Option 2: Faster approximation
def estimate_reverb_fast(y, sr):
    # Use only first 5 seconds
    y_sample = y[:sr*5]
    # Use simpler algorithm
    return "low" if simple_check(y_sample) else "high"
```

### 4. Optimize Room Tone
```python
# Before: Scan entire file
def detect_room_tone(y, sr):
    scan_duration = len(y) / sr  # Entire file

# After: Scan only edges
def detect_room_tone_fast(y, sr):
    scan_duration = 10  # Only first/last 10 seconds
    start = y[:sr*10]
    end = y[-sr*10:]
    # Analyze only these portions
```

---

## Browser-Based Architecture (Future Reference)

### Technology Stack
- **Web Audio API** - Native browser audio processing
- **AudioWorklet** - Low-latency audio processing in separate thread
- **WebAssembly** - Compile C/C++ libraries to browser-native code
- **Emscripten** - Toolchain to compile to WASM

### Libraries to Port/Use
- **LUFS calculation** - Port pyloudnorm to WASM
- **FFT analysis** - Use KissFFT (small, fast C library)
- **Basic metrics** - Pure JavaScript (fast enough)

### Example: RMS in Browser
```javascript
// Web Audio API approach
async function calculateRMS(audioBuffer) {
    const channelData = audioBuffer.getChannelData(0);
    let sum = 0;

    for (let i = 0; i < channelData.length; i++) {
        sum += channelData[i] * channelData[i];
    }

    const rms = Math.sqrt(sum / channelData.length);
    const rmsDB = 20 * Math.log10(rms);

    return rmsDB;
}
// Processes 1 minute of audio in ~50ms
```

---

## Performance Benchmarks (Estimated)

| File Size | Current | Quick Wins | Faster Tools | Browser | Sampling |
|-----------|---------|------------|--------------|---------|----------|
| 1 min WAV | 60s | 20s | 12s | 5s | 5s |
| 5 min MP3 | 180s | 60s | 35s | 8s | 5s |
| 30 min WAV | 900s | 300s | 180s | 25s | 5s |
| 2 hr audiobook | 3600s | 1200s | 720s | 90s | 5s |

---

## User Experience Improvements

Beyond raw speed, improve perceived performance:

### 1. Progress Indicators
- Show percentage complete
- Display which metric is being calculated
- Estimated time remaining

### 2. Partial Results
- Show file info immediately
- Display metrics as they complete (streaming)
- Don't wait for everything to finish

### 3. Queue System
- Allow multiple file uploads
- Process in background
- Show status for each file

### 4. Caching
- Remember previous analyses
- Show cached results instantly
- Re-analyze only if file changed

---

## Next Steps

1. **Benchmark Current Performance** - Measure exact timings for each operation
2. **Implement Quick Wins** - Start with downsampling and parallel processing
3. **A/B Test** - Compare accuracy of faster methods vs current approach
4. **User Feedback** - Survey users on acceptable trade-offs (speed vs accuracy)
5. **Gradual Rollout** - Offer "Fast Mode" as option before making default

---

## Resources

### FFmpeg Python Integration
- **ffmpeg-python**: https://github.com/kkroening/ffmpeg-python
- **pydub**: https://github.com/jiaaro/pydub

### Browser Audio Processing
- **Web Audio API Docs**: https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API
- **AudioWorklet Guide**: https://developers.google.com/web/updates/2017/12/audio-worklet

### WebAssembly Audio
- **Emscripten**: https://emscripten.org/
- **AudioWorklet + WASM**: https://github.com/GoogleChromeLabs/web-audio-samples

### Fast Audio Libraries
- **aubio**: https://aubio.org/
- **Essentia**: https://essentia.upf.edu/
- **librosa optimization tips**: https://librosa.org/doc/latest/ioformats.html

---

## Conclusion

The fastest path to improvement:
1. **Immediate** (1-2 hours): Implement downsampling + skip reverb → **2-3x faster**
2. **Short-term** (1-2 days): Add parallel processing + optimize room tone → **4-5x faster**
3. **Long-term** (1-2 weeks): Browser-based processing → **10-15x faster + zero server costs**

Recommended: Start with Quick Wins, measure impact, then decide if further optimization is needed based on user feedback.

---

**Last Updated:** October 22, 2025
