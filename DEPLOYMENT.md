# Deployment Guide

## Current Issue

The frontend is deployed on Vercel, but the backend services are not deployed. The frontend is trying to call `http://127.0.0.1:8000` which doesn't exist in production.

## Solution: Deploy Backend to Production

You have two options:

### Option 1: Deploy to Railway (Recommended - Easiest)

1. Go to https://railway.app
2. Create a new project
3. Connect your GitHub repository
4. Add a new service from your repo
5. Set the root directory to the project root (not rewriter-service or pdf-service)
6. Set environment variables:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `PORT`: Railway will set this automatically
7. Railway will auto-detect Python and install dependencies
8. Set the start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
9. Get the deployed URL (e.g., `https://your-app.railway.app`)
10. Update your frontend `.env` or `vite.config.ts` to use this URL

### Option 2: Deploy to Render

1. Go to https://render.com
2. Create a new Web Service
3. Connect your GitHub repository
4. Configure:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variable: `OPENAI_API_KEY`
6. Deploy and get the URL
7. Update frontend to use this URL

### Option 3: Use Vercel Serverless Functions (Advanced)

Vercel supports Python serverless functions, but WeasyPrint (PDF generation) requires system libraries that may not be available. This option is more complex.

## Update Frontend Configuration

After deploying the backend, update the frontend to point to your deployed backend:

1. Create a `.env.production` file:
```
VITE_BACKEND_URL=https://your-backend-url.railway.app
```

Or update `services/gemini.ts`:
```typescript
const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "https://your-backend-url.railway.app";
```

## Integrated Mode

The backend now supports **integrated mode** where it doesn't need separate microservices. It will:
- Use OpenAI directly for resume rewriting
- Use WeasyPrint directly for PDF generation
- Work as a single deployable service

This is the default when `REWRITER_URL` and `PDF_URL` environment variables are not set.

## Local Development

For local development with microservices:

```bash
# Terminal 1 - Rewriter Service
cd rewriter-service
source .venv/bin/activate
export OPENAI_API_KEY="your-key"
uvicorn main:app --port 8001 --reload

# Terminal 2 - PDF Service  
cd pdf-service
source .venv/bin/activate
uvicorn main:app --port 8002 --reload

# Terminal 3 - Gateway
source .venv/bin/activate
export REWRITER_URL="http://localhost:8001/generate"
export PDF_URL="http://localhost:8002/generate"
uvicorn main:app --port 8000 --reload

# Terminal 4 - Frontend
npm run dev
```

For local development with integrated mode (single service):

```bash
# Terminal 1 - Backend
source .venv/bin/activate
export OPENAI_API_KEY="your-key"
uvicorn main:app --port 8000 --reload

# Terminal 2 - Frontend
npm run dev
```

## Environment Variables

### Required for Production:
- `OPENAI_API_KEY`: Your OpenAI API key

### Optional (for microservice mode):
- `REWRITER_URL`: URL to rewriter microservice (default: None, uses integrated mode)
- `PDF_URL`: URL to PDF microservice (default: None, uses integrated mode)
- `USE_MICROSERVICES`: Set to "true" to enable microservice mode (default: "false")
- `REDIS_URL`: Redis connection string for session storage (optional)

## Notes

- The `node-domexception` warning is harmless and comes from a transitive dependency
- WeasyPrint requires system libraries that may need to be installed on the deployment platform
- For Railway/Render, the integrated mode (single service) is recommended for simplicity

