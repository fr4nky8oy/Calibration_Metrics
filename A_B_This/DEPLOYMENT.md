# A/B This - Deployment Guide

## Local API Server ✅ TESTED

Your API is now running locally at:
- **API Root:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/api/health

---

## Railway Deployment Steps

### 1. Install Railway CLI

```bash
# Using npm (if you have Node.js)
npm install -g @railway/cli

# Or using Homebrew
brew install railway
```

### 2. Login to Railway

```bash
railway login
```

This will open your browser to authenticate with Railway.

### 3. Initialize Railway Project

```bash
cd /Users/frankyredente/Music/Claude/CalibrationMetrics/A_B_This/backend
railway init
```

When prompted:
- **Project name:** `ab-this-backend` (or your preferred name)
- **Environment:** Select "production"

### 4. Link to Railway Project (if existing)

If you already have a Railway project:

```bash
railway link
```

Select your existing project from the list.

### 5. Set Environment Variables

```bash
# Set production environment variables
railway variables set ENVIRONMENT=production
railway variables set DEBUG=false
railway variables set CORS_ORIGINS='["https://your-frontend.vercel.app","http://localhost:3000"]'
railway variables set MAX_FILE_SIZE_MB=50
railway variables set DOWNSAMPLE_SR=22050
```

Or use the Railway dashboard:
1. Go to https://railway.app
2. Select your project
3. Go to "Variables" tab
4. Add the variables above

### 6. Deploy to Railway

```bash
railway up
```

This will:
- Build your Python application
- Install dependencies from `requirements.txt`
- Start the server using the command in `railway.json`

### 7. Get Your Deployed URL

```bash
railway domain
```

Or check the Railway dashboard for your public URL.

---

## Verify Deployment

Once deployed, test your API:

```bash
# Replace with your Railway URL
curl https://your-app.railway.app/api/health

# Should return:
# {"status":"healthy","app":"A/B This API","version":"0.1.0"}
```

---

## Railway Configuration

The `railway.json` file is already configured:

```json
{
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "pip install -r requirements.txt"
  },
  "deploy": {
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

Railway will automatically:
- Detect Python
- Install dependencies
- Set the `PORT` environment variable
- Start your FastAPI server

---

## Environment Variables (Production)

**Required Variables:**
- `ENVIRONMENT=production`
- `DEBUG=false`
- `CORS_ORIGINS=["https://your-frontend.vercel.app"]` (update with your Vercel domain)

**Optional Variables:**
- `MAX_FILE_SIZE_MB=50` (default)
- `DOWNSAMPLE_SR=22050` (default)
- `ANALYSIS_TIMEOUT=120` (default)

---

## Testing the Deployed API

### 1. Health Check

```bash
curl https://your-app.railway.app/api/health
```

### 2. API Documentation

Visit: `https://your-app.railway.app/docs`

This opens the interactive Swagger UI where you can:
- See all available endpoints
- Test the `/api/compare` endpoint with file uploads
- View request/response schemas

### 3. Test Comparison Endpoint

```bash
curl -X POST "https://your-app.railway.app/api/compare" \
  -H "Content-Type: multipart/form-data" \
  -F "your_mix=@/path/to/your_mix.wav" \
  -F "reference=@/path/to/reference.wav"
```

---

## Monitoring & Logs

### View Logs

```bash
railway logs
```

Or check the Railway dashboard:
1. Go to your project
2. Click "Deployments"
3. View real-time logs

### Check Deployment Status

```bash
railway status
```

---

## Cost Optimization

Railway hobby tier ($5/month) includes:
- 500 hours of execution time
- $5 worth of resources

**Tips to stay within budget:**
1. ✅ We already downsample audio to 22kHz (50% faster)
2. ✅ Max file size set to 50MB
3. ✅ Analysis times ~20-30 seconds
4. Consider: Sleep after 1 hour of inactivity (Railway feature)

**Expected usage:**
- ~100 comparisons/month = well within limits
- Processing time: ~30s per comparison
- Total compute: ~50 minutes/month

---

## Troubleshooting

### Deployment Fails

Check logs:
```bash
railway logs --tail 100
```

Common issues:
- Missing dependencies: Verify `requirements.txt`
- Port not set: Railway sets `$PORT` automatically
- Build timeout: Reduce dependencies or increase timeout

### CORS Errors

Update CORS_ORIGINS to include your frontend domain:
```bash
railway variables set CORS_ORIGINS='["https://your-frontend.vercel.app","http://localhost:3000"]'
```

### Out of Memory

Reduce max file size:
```bash
railway variables set MAX_FILE_SIZE_MB=30
```

Or upgrade to Railway Pro tier.

---

## Next Steps

1. ✅ Local API tested and working
2. ⏭️ Deploy to Railway
3. ⏭️ Get Railway URL
4. ⏭️ Build React frontend
5. ⏭️ Connect frontend to Railway backend
6. ⏭️ Deploy frontend to Vercel

---

## Support

- **Railway Docs:** https://docs.railway.app
- **Railway Discord:** https://discord.gg/railway
- **A/B This Issues:** Open an issue on GitHub

