# Fix Vercel Repository Mismatch

## Problem
- **Vercel is connected to:** `jonnrohith/klip-resume-ai`
- **Your local repo is:** `jonnrohith/klip-ai`
- **Error:** "The provided link points to a different repository"

## Solution: Reconnect Vercel to Correct Repository

### Step 1: Go to Vercel Project Settings
1. Open your Vercel dashboard
2. Click on your project
3. Go to **Settings** tab
4. Click **Git** in the left sidebar

### Step 2: Disconnect Current Repository
1. Scroll to the "Connected Git Repository" section
2. Click **Disconnect** or **Change Repository**
3. Confirm the disconnection

### Step 3: Connect Correct Repository
1. Click **Connect Git Repository**
2. Select **GitHub** (if not already selected)
3. Search for: `klip-ai`
4. Select: `jonnrohith/klip-ai`
5. Click **Connect**

### Step 4: Configure Project (if prompted)
- **Framework Preset:** `Vite`
- **Root Directory:** `./`
- **Build Command:** `npm run build`
- **Output Directory:** `dist`
- **Install Command:** `npm install`

### Step 5: Add Environment Variable
1. Go to **Settings** → **Environment Variables**
2. Add:
   - **Key:** `VITE_BACKEND_URL`
   - **Value:** `https://your-render-backend.onrender.com` (your Render backend URL)
   - **Environment:** Select all (Production, Preview, Development)
3. Click **Save**

### Step 6: Deploy
1. Go to **Deployments** tab
2. Click **Deploy** (or push to GitHub to trigger auto-deploy)
3. Wait for deployment to complete

## Alternative: Use Existing Repository

If you want to keep using `klip-resume-ai`:

1. Update your local remote:
   ```bash
   git remote set-url origin https://github.com/jonnrohith/klip-resume-ai.git
   ```

2. Push your code:
   ```bash
   git push origin main
   ```

3. Then deploy from Vercel using the connected repository

## Recommendation

**Use Option 1** (reconnect to `klip-ai`) since that's what you're working with locally. This keeps everything in sync.

