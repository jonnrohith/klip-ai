# Deploy Backend to Vercel

## Quick Setup

Your FastAPI backend is now configured to deploy on Vercel using serverless functions.

## Deployment Steps

### 1. Install Vercel CLI (if not already installed)
```bash
npm install -g vercel
```

### 2. Login to Vercel
```bash
vercel login
```

### 3. Deploy from Project Root
```bash
cd /path/to/resumate-ai
vercel
```

Follow the prompts:
- **Set up and deploy?** → Yes
- **Which scope?** → Your account
- **Link to existing project?** → No (or Yes if you want to link to existing)
- **What's your project's name?** → resumate-ai-backend (or your choice)
- **In which directory is your code located?** → `./` (current directory)

### 4. Set Environment Variables

After deployment, set your environment variables in Vercel Dashboard:

1. Go to your project → Settings → Environment Variables
2. Add:
   - `OPENAI_API_KEY` = `your-openai-api-key`

### 5. Production Deployment

For production deployment:
```bash
vercel --prod
```

## Configuration

The `vercel.json` file is already configured:
- Uses `@vercel/python` builder
- Routes all requests to `main.py`
- FastAPI app is automatically detected

## Important Notes

### ✅ What Works
- FastAPI endpoints (`/upload`, `/result/{session_id}`, `/healthz`)
- OpenAI integration for resume rewriting
- HTML resume generation
- Session storage (in-memory)

### ⚠️ Limitations
- **WeasyPrint (PDF generation)**: May not work in Vercel's serverless environment due to missing system libraries (Cairo, Pango, etc.)
  - The app handles this gracefully - PDF generation will be disabled if WeasyPrint fails
  - HTML resume will still be available
  - Users can still view and copy the resume

### 🔧 If PDF Generation is Critical
Consider:
1. Using a separate service for PDF generation (e.g., Render, Railway)
2. Using a client-side PDF library (jsPDF) - already in your frontend
3. Using an external PDF API service

## Testing

After deployment, test your endpoints:
- Health check: `https://your-project.vercel.app/healthz`
- API docs: `https://your-project.vercel.app/docs`
- Upload endpoint: `https://your-project.vercel.app/upload`

## Update Frontend

Update your frontend to use the Vercel backend URL:

1. In Vercel Dashboard → Your Frontend Project → Environment Variables
2. Add: `VITE_BACKEND_URL` = `https://your-backend-project.vercel.app`

Or update `services/gemini.ts`:
```typescript
const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "https://your-backend-project.vercel.app";
```

## Troubleshooting

### Build Fails
- Check that `main.py` is in the root directory
- Ensure `requirements.txt` has all dependencies
- Check Vercel build logs for specific errors

### WeasyPrint Errors
- This is expected in serverless environments
- The app will continue to work without PDF generation
- Check logs to confirm: "WeasyPrint not available"

### Timeout Issues
- Vercel serverless functions have a 10s timeout on Hobby plan
- Pro plan has 60s timeout
- For longer operations, consider upgrading or using a different platform

## Deployment Commands

```bash
# Deploy to preview
vercel

# Deploy to production
vercel --prod

# View deployments
vercel ls

# View logs
vercel logs
```

