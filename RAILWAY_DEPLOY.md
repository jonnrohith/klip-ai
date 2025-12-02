# Railway Deployment Guide

## Quick Fix for Build Errors

The build was failing because `requirements.txt` included spaCy and the large `en-core-web-lg` model (587MB), which aren't needed in integrated mode.

### ✅ Fixed
- Removed spaCy from `requirements.txt` (not needed for integrated OpenAI mode)
- WeasyPrint is included but will gracefully fail if system libraries aren't available
- PDF generation is optional - the app works without it

## Deploy Steps

1. **Push the latest changes** (already done)

2. **In Railway Dashboard:**
   - Go to your service
   - Click "Redeploy" or wait for auto-deploy
   - The build should now succeed without spaCy

3. **If WeasyPrint fails:**
   - The app will still work, but PDF download will be disabled
   - You'll see a warning in logs: "WeasyPrint not available"
   - HTML resume will still be generated and downloadable

4. **To enable PDF generation (optional):**
   - Railway/Nixpacks should auto-install WeasyPrint system dependencies
   - If it still fails, we can add a custom buildpack

## Environment Variables

Make sure you have set:
- `OPENAI_API_KEY`: Your OpenAI API key (required)

## Testing

After deployment, test:
- Health check: `https://your-app.railway.app/healthz`
- API docs: `https://your-app.railway.app/docs`

## Troubleshooting

### Build still failing?
- Check Railway logs for specific error
- WeasyPrint might need system libraries - this is OK, PDF will be disabled

### PDF generation not working?
- Check logs for WeasyPrint errors
- This is expected if system libraries aren't available
- HTML resume still works fine

### Need spaCy for old microservice mode?
- Uncomment spaCy lines in `requirements.txt`
- But integrated mode doesn't need it

