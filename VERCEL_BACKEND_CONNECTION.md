# How to Connect Backend to Vercel Frontend

## Overview
- **Backend:** Deployed on Render (e.g., `https://your-backend.onrender.com`)
- **Frontend:** Deployed on Vercel
- **Connection:** Frontend needs to know the backend URL via environment variable

---

## Step-by-Step: Add Backend URL to Vercel

### Step 1: Get Your Backend URL from Render
1. Go to https://dashboard.render.com
2. Click on your backend service
3. Copy the URL (e.g., `https://resumate-ai-backend.onrender.com`)

### Step 2: Go to Vercel Project Settings
1. Go to https://vercel.com/dashboard
2. Click on your **frontend project**
3. Click on **Settings** tab (top navigation)

### Step 3: Add Environment Variable
1. In the left sidebar, click **Environment Variables**
2. You'll see a form to add new variables

### Step 4: Configure the Variable
Fill in the form:
- **Key:** `VITE_BACKEND_URL`
- **Value:** Your Render backend URL (e.g., `https://resumate-ai-backend.onrender.com`)
- **Environment:** Select all three:
  - ☑️ Production
  - ☑️ Preview  
  - ☑️ Development

### Step 5: Save
1. Click **Save** button
2. You'll see the variable appear in the list

### Step 6: Redeploy Frontend
After adding the environment variable, you need to redeploy:

**Option A: Automatic Redeploy**
- Push a new commit to GitHub
- Vercel will auto-deploy with the new environment variable

**Option B: Manual Redeploy**
1. Go to **Deployments** tab
2. Find your latest deployment
3. Click the **⋯** (three dots) menu
4. Click **Redeploy**
5. Confirm the redeploy

---

## Visual Guide

```
Vercel Dashboard
├── Your Project
    ├── Settings (tab)
        ├── Environment Variables (left sidebar)
            ├── Add New
                ├── Key: VITE_BACKEND_URL
                ├── Value: https://your-backend.onrender.com
                └── Environment: ☑️ All (Production, Preview, Development)
```

---

## Verify It's Working

### Check 1: Environment Variable is Set
1. Go to **Settings** → **Environment Variables**
2. You should see `VITE_BACKEND_URL` in the list

### Check 2: Frontend Uses Backend
1. Open your Vercel frontend URL
2. Open browser DevTools (F12)
3. Go to **Console** tab
4. Upload a resume
5. Go to **Network** tab
6. Look for requests to your Render backend URL
7. They should be successful (status 200)

### Check 3: Test Full Flow
1. Upload a resume on your Vercel frontend
2. Add a job description
3. Click "Optimize"
4. It should process successfully using the Render backend

---

## Important Notes

### ⚠️ No Trailing Slash
Make sure your backend URL **doesn't have a trailing slash**:
- ✅ Correct: `https://your-backend.onrender.com`
- ❌ Wrong: `https://your-backend.onrender.com/`

### ⚠️ HTTP vs HTTPS
Always use `https://` (not `http://`) for production:
- ✅ Correct: `https://your-backend.onrender.com`
- ❌ Wrong: `http://your-backend.onrender.com`

### ⚠️ Redeploy Required
After adding/changing environment variables, you **must redeploy** for changes to take effect.

---

## Troubleshooting

### Problem: Frontend still uses old backend URL
**Solution:**
1. Verify environment variable is set correctly
2. Redeploy the frontend
3. Clear browser cache and try again

### Problem: CORS errors
**Solution:**
- Backend already has CORS enabled
- Check that backend URL is correct
- Verify backend is running (check Render dashboard)

### Problem: 404 errors when calling backend
**Solution:**
1. Verify backend URL is correct
2. Test backend directly: `https://your-backend.onrender.com/docs`
3. Make sure backend is not sleeping (Render free tier spins down)

---

## Quick Reference

**Where to add:** Vercel Dashboard → Your Project → Settings → Environment Variables

**Variable name:** `VITE_BACKEND_URL`

**Variable value:** Your Render backend URL (e.g., `https://resumate-ai-backend.onrender.com`)

**After adding:** Redeploy the frontend

---

## Summary

1. ✅ Deploy backend to Render → Get backend URL
2. ✅ Go to Vercel → Settings → Environment Variables
3. ✅ Add `VITE_BACKEND_URL` with your Render backend URL
4. ✅ Redeploy frontend
5. ✅ Test the connection

That's it! Your frontend will now connect to your backend. 🚀

