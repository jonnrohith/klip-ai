# 🚀 Quick Deployment Guide

## Step-by-Step: Deploy Backend to Render + Frontend to Vercel

---

## 📦 Part 1: Deploy Backend to Render

### Step 1: Prepare Your Repository
✅ Make sure all changes are committed and pushed to GitHub:
```bash
git add .
git commit -m "Ready for deployment"
git push
```

### Step 2: Create Render Account
1. Go to https://render.com
2. Sign up with GitHub (recommended) or email
3. Verify your email if needed

### Step 3: Create New Web Service on Render

1. **Click "New +" → "Web Service"**

2. **Connect Repository:**
   - Select your GitHub repository: `klip-ai` (or your repo name)
   - Click "Connect"

3. **Configure Service:**
   - **Name:** `resumate-ai-backend` (or any name you prefer)
   - **Region:** Choose closest to your users (e.g., `Oregon (US West)`)
   - **Branch:** `main` (or your default branch)
   - **Root Directory:** Leave empty (or `./` if needed)
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type:** `Free` (or upgrade later)

4. **Add Environment Variables:**
   - Click "Add Environment Variable"
   - **Key:** `OPENAI_API_KEY`
   - **Value:** Your OpenAI API key (starts with `sk-...`)
   - Click "Add"

5. **Advanced Settings (Optional):**
   - **Health Check Path:** `/healthz` (if you have one)
   - **Auto-Deploy:** `Yes` (deploys on every push)

6. **Click "Create Web Service"**

### Step 4: Wait for Deployment
- Render will build and deploy your service
- This takes 5-10 minutes
- Watch the logs for any errors

### Step 5: Get Your Backend URL
- Once deployed, you'll see: `https://your-service-name.onrender.com`
- **Copy this URL** - you'll need it for the frontend!

### Step 6: Test Your Backend
1. Open: `https://your-service-name.onrender.com/docs`
   - Should show FastAPI Swagger UI
2. Open: `https://your-service-name.onrender.com/healthz`
   - Should return: `{"status":"ok"}`

---

## 🎨 Part 2: Deploy Frontend to Vercel

### Step 1: Prepare Frontend
✅ Make sure frontend code is committed and pushed to GitHub

### Step 2: Create Vercel Account
1. Go to https://vercel.com
2. Sign up with GitHub (recommended)
3. Authorize Vercel to access your repositories

### Step 3: Import Project to Vercel

1. **Click "Add New..." → "Project"**

2. **Import Repository:**
   - Select your GitHub repository
   - Click "Import"

3. **Configure Project:**
   - **Framework Preset:** `Vite` (should auto-detect)
   - **Root Directory:** `./` (leave as is)
   - **Build Command:** `npm run build` (should auto-fill)
   - **Output Directory:** `dist` (should auto-fill)
   - **Install Command:** `npm install` (should auto-fill)

4. **Add Environment Variables:**
   - Click "Environment Variables"
   - **Key:** `VITE_BACKEND_URL`
   - **Value:** `https://your-service-name.onrender.com` (from Step 5 above)
   - **Environment:** Select all (Production, Preview, Development)
   - Click "Add"

5. **Click "Deploy"**

### Step 4: Wait for Deployment
- Vercel will build and deploy your frontend
- This takes 2-5 minutes
- Watch the build logs

### Step 5: Get Your Frontend URL
- Once deployed, you'll see: `https://your-project-name.vercel.app`
- **This is your live app!** 🎉

---

## ✅ Part 3: Verify Everything Works

### Test 1: Check Backend
```bash
# Health check
curl https://your-service-name.onrender.com/healthz

# Should return: {"status":"ok"}
```

### Test 2: Check Frontend
1. Open your Vercel URL: `https://your-project-name.vercel.app`
2. Open browser DevTools (F12)
3. Go to **Console** tab
4. Check for any errors

### Test 3: Test Full Flow
1. Go to your Vercel frontend
2. Upload a resume
3. Add a job description (optional)
4. Click "Optimize"
5. Check if it processes correctly
6. Try downloading the PDF

### Test 4: Check Network Requests
1. Open DevTools → **Network** tab
2. Upload a resume
3. Look for requests to `your-service-name.onrender.com`
4. Verify they're successful (status 200)

---

## 🔧 Troubleshooting

### Backend Issues

**Problem: Build fails on Render**
- ✅ Check Render logs for specific errors
- ✅ Verify `requirements.txt` is correct
- ✅ Make sure Python version is compatible (3.11+)

**Problem: Service returns 404**
- ✅ This is normal for root `/` route
- ✅ Test `/docs` or `/healthz` instead

**Problem: "OPENAI_API_KEY not set" error**
- ✅ Go to Render Dashboard → Your Service → Environment
- ✅ Verify `OPENAI_API_KEY` is set correctly
- ✅ Redeploy after adding environment variable

**Problem: Service spins down (free tier)**
- ✅ Free tier spins down after 15 min inactivity
- ✅ First request takes 30-50 seconds (cold start)
- ✅ Consider upgrading to paid plan ($7/month) for always-on

### Frontend Issues

**Problem: Frontend can't connect to backend**
- ✅ Check `VITE_BACKEND_URL` in Vercel environment variables
- ✅ Make sure URL doesn't have trailing slash
- ✅ Verify backend is running (check Render dashboard)

**Problem: CORS errors**
- ✅ Backend already has CORS enabled
- ✅ Check browser console for specific error
- ✅ Verify backend URL is correct

**Problem: Build fails on Vercel**
- ✅ Check Vercel build logs
- ✅ Verify `package.json` is correct
- ✅ Make sure all dependencies are listed

---

## 📝 Environment Variables Summary

### Render (Backend)
- `OPENAI_API_KEY` - Your OpenAI API key (required)

### Vercel (Frontend)
- `VITE_BACKEND_URL` - Your Render backend URL (required)
  - Example: `https://resumate-ai-backend.onrender.com`

---

## 🎯 Quick Reference

### Backend URLs
- **Render Dashboard:** https://dashboard.render.com
- **Your Backend:** `https://your-service-name.onrender.com`
- **API Docs:** `https://your-service-name.onrender.com/docs`

### Frontend URLs
- **Vercel Dashboard:** https://vercel.com/dashboard
- **Your Frontend:** `https://your-project-name.vercel.app`

---

## 🚀 After Deployment

### Optional: Custom Domain
- **Render:** Add custom domain in service settings
- **Vercel:** Add custom domain in project settings

### Optional: Monitor Logs
- **Render:** Dashboard → Your Service → Logs
- **Vercel:** Dashboard → Your Project → Deployments → View Function Logs

### Optional: Set Up Auto-Deploy
- Both platforms auto-deploy on git push (if enabled)
- Make sure your main branch is connected

---

## ✅ Checklist

### Backend (Render)
- [ ] Repository connected to Render
- [ ] Service created and configured
- [ ] `OPENAI_API_KEY` environment variable set
- [ ] Service deployed successfully
- [ ] Backend URL copied
- [ ] `/docs` endpoint accessible
- [ ] `/healthz` endpoint returns `{"status":"ok"}`

### Frontend (Vercel)
- [ ] Repository connected to Vercel
- [ ] Project imported and configured
- [ ] `VITE_BACKEND_URL` environment variable set
- [ ] Frontend deployed successfully
- [ ] Frontend URL accessible
- [ ] No console errors
- [ ] Can upload resume and process it

---

## 🎉 You're Done!

Your app should now be live:
- **Backend:** `https://your-service-name.onrender.com`
- **Frontend:** `https://your-project-name.vercel.app`

Test it out and enjoy! 🚀

---

## 💡 Pro Tips

1. **Monitor Both Platforms:** Check logs regularly for errors
2. **Use Environment Variables:** Never hardcode URLs or API keys
3. **Test Before Deploying:** Test locally first with `npm run dev` and `uvicorn main:app --reload`
4. **Keep Backend URL Updated:** If you redeploy backend, update `VITE_BACKEND_URL` in Vercel
5. **Free Tier Limits:** Render free tier spins down after inactivity - first request will be slow

---

## 📞 Need Help?

- **Render Docs:** https://render.com/docs
- **Vercel Docs:** https://vercel.com/docs
- **Check Logs:** Both platforms have detailed logs in their dashboards

