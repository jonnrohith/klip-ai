# Render Deployment Setup Guide

## ✅ Your Backend is Live!

Your backend is successfully deployed at: **https://klip-ai.onrender.com**

### About the 404 Errors

The 404 errors you see are **NORMAL** and **EXPECTED**:
- FastAPI doesn't have a root route `/` defined
- The service is working fine
- These are just health checks from Render

### Test Your Backend

Try these URLs to verify it's working:

1. **Health Check:**
   ```
   https://klip-ai.onrender.com/healthz
   ```
   Should return: `{"status":"ok"}`

2. **API Documentation:**
   ```
   https://klip-ai.onrender.com/docs
   ```
   Should show FastAPI Swagger UI

3. **Alternative Docs:**
   ```
   https://klip-ai.onrender.com/redoc
   ```
   Should show ReDoc documentation

---

## 🔗 Connect Vercel Frontend to Render Backend

### Step 1: Update Vercel Environment Variables

1. Go to your **Vercel Dashboard**
2. Select your **frontend project**
3. Go to **Settings** → **Environment Variables**
4. Add/Update:
   - **Name:** `VITE_BACKEND_URL`
   - **Value:** `https://klip-ai.onrender.com`
   - **Environment:** Production, Preview, Development (select all)

### Step 2: Redeploy Frontend

After adding the environment variable:

1. Go to **Deployments** tab
2. Click **⋯** (three dots) on latest deployment
3. Click **Redeploy**
4. Or push a new commit to trigger auto-deploy

### Step 3: Verify Connection

1. Open your Vercel frontend URL
2. Try uploading a resume
3. Check browser console (F12) for any errors
4. Check Network tab to see if requests go to Render backend

---

## 🔧 Alternative: Update Code Directly

If you prefer to hardcode the backend URL (not recommended for production):

**File:** `services/gemini.ts`

```typescript
const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "https://klip-ai.onrender.com";
```

Then commit and push:
```bash
git add services/gemini.ts
git commit -m "Update backend URL to Render"
git push
```

---

## 🧪 Testing Your Setup

### Test Backend Endpoints:

```bash
# Health check
curl https://klip-ai.onrender.com/healthz

# Should return: {"status":"ok"}

# API docs
# Open in browser: https://klip-ai.onrender.com/docs
```

### Test Frontend → Backend:

1. Open your Vercel frontend
2. Open browser DevTools (F12)
3. Go to Network tab
4. Upload a resume
5. Check if requests go to `klip-ai.onrender.com`

---

## ⚠️ Important Notes

### Render Free Tier:
- **Spins down after 15 minutes** of inactivity
- First request after spin-down takes ~30-50 seconds (cold start)
- Subsequent requests are fast
- **Solution:** Upgrade to paid plan ($7/month) for always-on

### CORS:
- Your backend already has CORS enabled (`allow_origins=["*"]`)
- Should work with Vercel frontend automatically

### Environment Variables on Render:
- Make sure `OPENAI_API_KEY` is set in Render dashboard
- Go to: Render Dashboard → Your Service → Environment

---

## 🐛 Troubleshooting

### Backend not responding?
1. Check Render logs: Render Dashboard → Your Service → Logs
2. Verify `OPENAI_API_KEY` is set
3. Check if service is running (not sleeping)

### Frontend can't connect?
1. Check browser console for CORS errors
2. Verify `VITE_BACKEND_URL` is set in Vercel
3. Check Network tab to see actual request URL
4. Make sure backend URL doesn't have trailing slash

### 404 errors?
- These are normal for root `/` route
- Test `/healthz` or `/docs` instead

---

## 📊 Your Setup Summary

- **Backend:** Render (https://klip-ai.onrender.com)
- **Frontend:** Vercel (your-frontend.vercel.app)
- **Connection:** Frontend → Backend via `VITE_BACKEND_URL`

---

## 🚀 Next Steps

1. ✅ Backend deployed on Render
2. ✅ Set `VITE_BACKEND_URL` in Vercel
3. ✅ Redeploy frontend
4. ✅ Test the full flow
5. ⚠️ Consider upgrading Render for always-on (optional)

---

## 💡 Pro Tips

1. **Monitor Render Logs:** Check Render dashboard for any errors
2. **Test Locally First:** Use `http://127.0.0.1:8000` for local dev
3. **Use Environment Variables:** Don't hardcode URLs
4. **Check CORS:** If issues, verify CORS settings in `main.py`

