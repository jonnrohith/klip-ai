# Frontend Troubleshooting Guide

## Common Issues and Solutions

### Issue 1: Frontend Not Loading / Blank Page

**Symptoms:**
- Blank white page
- Console errors
- Page not loading

**Solutions:**

1. **Check Browser Console (F12)**
   - Look for JavaScript errors
   - Check Network tab for failed requests

2. **Verify Build Succeeded**
   - Check Vercel deployment logs
   - Look for build errors

3. **Check Environment Variables**
   - Vercel Dashboard → Settings → Environment Variables
   - Ensure `VITE_BACKEND_URL` is set to `https://klip-ai.onrender.com`

---

### Issue 2: Frontend Loads But Can't Connect to Backend

**Symptoms:**
- Frontend loads but shows errors when uploading
- "Failed to process resume" error
- Network errors in console

**Solutions:**

1. **Check Backend URL**
   ```typescript
   // In browser console, check:
   console.log(import.meta.env.VITE_BACKEND_URL);
   // Should show: https://klip-ai.onrender.com
   ```

2. **Verify Backend is Running**
   ```bash
   curl https://klip-ai.onrender.com/healthz
   # Should return: {"status":"ok"}
   ```

3. **Check CORS**
   - Backend has CORS enabled (`allow_origins=["*"]`)
   - If still issues, check browser console for CORS errors

4. **Render Free Tier Cold Start**
   - First request after 15 min inactivity takes 30-50 seconds
   - Wait for backend to wake up
   - Or upgrade to paid plan for always-on

---

### Issue 3: Environment Variable Not Working

**Symptoms:**
- Frontend still uses `http://127.0.0.1:8000`
- Requests going to wrong URL

**Solutions:**

1. **Set in Vercel Dashboard:**
   - Settings → Environment Variables
   - Name: `VITE_BACKEND_URL`
   - Value: `https://klip-ai.onrender.com`
   - **Important:** Select all environments (Production, Preview, Development)

2. **Redeploy After Adding Variable:**
   - Go to Deployments
   - Click ⋯ on latest deployment
   - Click Redeploy
   - Or push a new commit

3. **Verify in Build Logs:**
   - Check Vercel build logs
   - Should see environment variable being used

---

### Issue 4: Build Errors

**Symptoms:**
- Deployment fails
- Build errors in Vercel logs

**Solutions:**

1. **Check for Missing Dependencies**
   ```bash
   npm install
   npm run build
   ```

2. **Check TypeScript Errors**
   ```bash
   npx tsc --noEmit
   ```

3. **Check Vercel Build Logs**
   - Look for specific error messages
   - Common issues: missing files, import errors

---

### Issue 5: "Failed to process resume" Error

**Symptoms:**
- Error message appears when uploading
- Backend connection fails

**Solutions:**

1. **Check Backend Status**
   - Visit: https://klip-ai.onrender.com/healthz
   - Should return: `{"status":"ok"}`

2. **Check Render Logs**
   - Render Dashboard → Your Service → Logs
   - Look for errors or missing `OPENAI_API_KEY`

3. **Verify OpenAI API Key**
   - Render Dashboard → Environment
   - Ensure `OPENAI_API_KEY` is set

4. **Check Network Tab**
   - Browser DevTools → Network
   - See actual request/response
   - Check for 500/502/503 errors

---

## Quick Diagnostic Steps

### Step 1: Test Backend
```bash
# Health check
curl https://klip-ai.onrender.com/healthz

# API docs
# Open: https://klip-ai.onrender.com/docs
```

### Step 2: Check Frontend Console
1. Open your Vercel frontend URL
2. Press F12 (DevTools)
3. Check Console tab for errors
4. Check Network tab for failed requests

### Step 3: Verify Environment Variable
1. In browser console, run:
   ```javascript
   console.log(import.meta.env.VITE_BACKEND_URL);
   ```
2. Should show: `https://klip-ai.onrender.com`
3. If shows `undefined`, environment variable not set

### Step 4: Test Full Flow
1. Upload a resume
2. Watch Network tab
3. Should see request to `klip-ai.onrender.com/upload`
4. Check response status (should be 200)

---

## Common Error Messages

### "Failed to process resume. Please ensure you have a valid API Key"
- **Cause:** Backend can't connect to OpenAI
- **Fix:** Check `OPENAI_API_KEY` in Render environment variables

### "Backend /upload failed: 502"
- **Cause:** Backend service down or error
- **Fix:** Check Render logs, verify service is running

### "Backend /upload failed: 503"
- **Cause:** Backend service sleeping (free tier)
- **Fix:** Wait 30-50 seconds for cold start, or upgrade Render plan

### "CORS policy: No 'Access-Control-Allow-Origin' header"
- **Cause:** CORS not configured (but it should be)
- **Fix:** Check `main.py` has CORS middleware enabled

### "NetworkError when attempting to fetch resource"
- **Cause:** Backend URL incorrect or backend down
- **Fix:** Verify backend URL, check backend status

---

## Debugging Checklist

- [ ] Backend health check works: `https://klip-ai.onrender.com/healthz`
- [ ] Backend API docs accessible: `https://klip-ai.onrender.com/docs`
- [ ] `VITE_BACKEND_URL` set in Vercel environment variables
- [ ] Frontend redeployed after setting environment variable
- [ ] Browser console shows correct backend URL
- [ ] Network tab shows requests to Render backend
- [ ] `OPENAI_API_KEY` set in Render environment
- [ ] No CORS errors in browser console
- [ ] Render service is running (not sleeping)

---

## Still Not Working?

1. **Check Vercel Deployment Logs**
   - Vercel Dashboard → Deployments → Latest → View Logs

2. **Check Render Service Logs**
   - Render Dashboard → Your Service → Logs

3. **Test Backend Directly**
   ```bash
   curl -X POST https://klip-ai.onrender.com/upload \
     -F "original_resume=@test.txt" \
     -F "job_description=test"
   ```

4. **Check Browser Console**
   - Full error messages
   - Network request details
   - Response status codes

---

## Quick Fix: Update Default URL

If environment variable isn't working, the code now defaults to Render:

```typescript
// services/gemini.ts
const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "https://klip-ai.onrender.com";
```

This means even without the environment variable, it will use Render backend.

