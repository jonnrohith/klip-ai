# Local Testing Guide

## Prerequisites

1. **Python 3.11+** installed
2. **Node.js** installed
3. **OpenAI API Key** ready

---

## Step 1: Set Up Backend (Local)

### 1.1 Create Virtual Environment

```bash
# In project root
python3.11 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 1.2 Install Dependencies

```bash
pip install -r requirements.txt
```

### 1.3 Set Environment Variable

```bash
export OPENAI_API_KEY="your-openai-api-key-here"
```

### 1.4 Start Backend Server

```bash
uvicorn main:app --port 8000 --reload
```

**Expected Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 1.5 Test Backend

Open in browser:
- **Health Check:** http://127.0.0.1:8000/healthz (should show `{"status":"ok"}`)
- **API Docs:** http://127.0.0.1:8000/docs (should show FastAPI Swagger UI)

---

## Step 2: Set Up Frontend (Local)

### 2.1 Install Dependencies

```bash
# In project root (new terminal)
npm install
```

### 2.2 Start Frontend Dev Server

```bash
npm run dev
```

**Expected Output:**
```
  VITE v6.x.x  ready in xxx ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
```

### 2.3 Verify Frontend Configuration

The frontend is already configured to use `http://127.0.0.1:8000` as default backend URL (see `services/gemini.ts`).

---

## Step 3: Test the Full Flow

### 3.1 Open Frontend

Open browser: **http://localhost:3000**

### 3.2 Test Upload

1. Upload a resume file (or paste text)
2. Enter a job description
3. Click "Optimize"
4. Wait for processing
5. Check if resume is rewritten and displayed

### 3.3 Check Browser Console

1. Press **F12** to open DevTools
2. Go to **Console** tab - should see no errors
3. Go to **Network** tab - should see requests to `http://127.0.0.1:8000`

---

## Troubleshooting

### Backend Not Starting?

**Error: `ModuleNotFoundError: No module named 'fastapi'`**
```bash
# Make sure virtual environment is activated
source .venv/bin/activate
pip install -r requirements.txt
```

**Error: `OPENAI_API_KEY not set`**
```bash
export OPENAI_API_KEY="your-key-here"
# Verify it's set:
echo $OPENAI_API_KEY
```

**Error: Port 8000 already in use**
```bash
# Use a different port:
uvicorn main:app --port 8001 --reload
# Then update services/gemini.ts to use port 8001
```

### Frontend Not Starting?

**Error: `npm: command not found`**
- Install Node.js from https://nodejs.org

**Error: Port 3000 already in use**
- Vite will automatically use the next available port
- Or kill the process using port 3000

### Frontend Can't Connect to Backend?

**Error: `Failed to fetch` or `NetworkError`**
1. Check backend is running: http://127.0.0.1:8000/healthz
2. Check backend URL in `services/gemini.ts`:
   ```typescript
   const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "http://127.0.0.1:8000";
   ```
3. Check browser console for CORS errors (shouldn't happen, CORS is enabled)

**Error: `Failed to process resume`**
1. Check backend logs for errors
2. Verify `OPENAI_API_KEY` is set correctly
3. Check OpenAI API key is valid

---

## Quick Test Commands

### Test Backend Health
```bash
curl http://127.0.0.1:8000/healthz
# Should return: {"status":"ok"}
```

### Test Backend Upload (from terminal)
```bash
curl -X POST http://127.0.0.1:8000/upload \
  -F "original_resume=@test_resume.txt" \
  -F "job_description=Software Engineer"
```

### Check Frontend Backend URL
```javascript
// In browser console (F12):
console.log(import.meta.env.VITE_BACKEND_URL);
// Should show: undefined (uses default http://127.0.0.1:8000)
```

---

## Local Development Setup Summary

**Terminal 1 - Backend:**
```bash
cd /path/to/resumate-ai
source .venv/bin/activate
export OPENAI_API_KEY="your-key"
uvicorn main:app --port 8000 --reload
```

**Terminal 2 - Frontend:**
```bash
cd /path/to/resumate-ai
npm run dev
```

**Browser:**
- Frontend: http://localhost:3000
- Backend API: http://127.0.0.1:8000/docs

---

## What to Test

- [ ] Backend starts without errors
- [ ] Backend health endpoint works
- [ ] Frontend loads correctly
- [ ] Can upload resume file
- [ ] Can paste resume text
- [ ] Can enter job description
- [ ] Resume processing works
- [ ] Rewritten resume displays
- [ ] PDF download works (if WeasyPrint available)
- [ ] No console errors
- [ ] Network requests succeed

---

## Ready for Deployment?

Once everything works locally:
1. ✅ Backend tested and working
2. ✅ Frontend tested and working
3. ✅ Full flow tested end-to-end
4. ✅ No errors in console/logs

Then you can deploy:
- **Backend:** Already on Render (https://klip-ai.onrender.com)
- **Frontend:** Deploy to Vercel (will auto-deploy on push)

