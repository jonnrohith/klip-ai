# Fix: OPENAI_API_KEY Not Set on Render

## Error Message
```
Failed to process resume. Please ensure you have a valid API Key and try again. 
Backend /upload failed: 503 {"detail":"OPENAI_API_KEY environment variable is not set. Please configure it."}
```

## Solution: Add OPENAI_API_KEY to Render

### Step 1: Go to Render Dashboard
1. Go to https://dashboard.render.com
2. Log in to your account

### Step 2: Open Your Backend Service
1. Click on your backend service (the one you deployed)
2. You should see the service dashboard

### Step 3: Go to Environment Tab
1. In the left sidebar, click **Environment**
2. Or look for **Environment Variables** section

### Step 4: Add Environment Variable
1. Click **Add Environment Variable** button
2. Fill in:
   - **Key:** `OPENAI_API_KEY`
   - **Value:** Your OpenAI API key (starts with `sk-...`)
   - **Apply changes when:** Select "Save and Deploy" or "Save Only"

### Step 5: Save and Deploy
1. Click **Save Changes**
2. If you selected "Save and Deploy", Render will automatically redeploy
3. If you selected "Save Only", go to **Manual Deploy** → **Deploy latest commit**

### Step 6: Wait for Deployment
- Render will rebuild and redeploy your service
- This takes 5-10 minutes
- Watch the logs to see progress

### Step 7: Verify It's Working
1. Once deployed, test your backend:
   ```bash
   curl https://your-backend.onrender.com/healthz
   ```
   Should return: `{"status":"ok"}`

2. Test from your Vercel frontend:
   - Upload a resume
   - It should now process successfully

---

## Where to Find Your OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Log in to your OpenAI account
3. Click **Create new secret key** (or use existing one)
4. Copy the key (starts with `sk-...`)
5. **Important:** Save it somewhere safe - you can't see it again!

---

## Visual Guide

```
Render Dashboard
├── Your Backend Service
    ├── Environment (left sidebar)
        ├── Add Environment Variable
            ├── Key: OPENAI_API_KEY
            ├── Value: sk-... (your API key)
            └── Save Changes
```

---

## Important Notes

### ⚠️ Security
- Never commit your API key to Git
- Never share your API key publicly
- Only add it in Render's environment variables (secure)

### ⚠️ After Adding
- You must redeploy for the change to take effect
- The service will restart with the new environment variable

### ⚠️ Format
- The key should start with `sk-`
- No spaces or quotes needed
- Just paste the key directly

---

## Troubleshooting

### Problem: Still getting the error after adding
**Solutions:**
1. Make sure you saved the environment variable
2. Make sure you redeployed after adding it
3. Check Render logs for any errors
4. Verify the key is correct (no extra spaces)

### Problem: Don't have an OpenAI API key
**Solution:**
1. Go to https://platform.openai.com/signup
2. Create an account
3. Add payment method (required for API access)
4. Go to API Keys section
5. Create a new key

### Problem: Service not redeploying
**Solution:**
1. Go to **Manual Deploy** tab
2. Click **Deploy latest commit**
3. Or push a new commit to trigger auto-deploy

---

## Quick Checklist

- [ ] Have OpenAI API key ready
- [ ] Go to Render Dashboard → Your Service
- [ ] Click **Environment** tab
- [ ] Add `OPENAI_API_KEY` with your key
- [ ] Save and redeploy
- [ ] Wait for deployment to complete
- [ ] Test from frontend

---

## Summary

The error means Render doesn't have your OpenAI API key. Add it in:
**Render Dashboard → Your Service → Environment → Add Environment Variable**

After adding and redeploying, your backend will be able to process resumes! 🚀

