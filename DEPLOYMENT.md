# Deployment Guide

## Backend Deployment

The backend is a FastAPI application that can be deployed to any platform that supports Python.

### General Deployment Steps

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Environment Variables:**
   - `OPENAI_API_KEY`: Your OpenAI API key (required)

3. **Start the Server:**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port $PORT
   ```
   (Replace `$PORT` with your platform's port variable or a specific port like `8000`)

### Platform-Specific Deployment

#### Deploy to Render
1. Go to https://render.com
2. Create a new Web Service
3. Connect your GitHub repository
4. Configure:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variable: `OPENAI_API_KEY`
6. Deploy and get the URL

#### Deploy to Other Platforms
- **Heroku**: Use `Procfile` (create one if needed)
- **DigitalOcean App Platform**: Configure build and start commands
- **AWS/GCP/Azure**: Use container deployment or serverless functions

## Frontend Configuration

After deploying the backend, update the frontend to point to your deployed backend:

1. Create a `.env.production` file:
```
VITE_BACKEND_URL=https://your-backend-url.com
```

Or update `services/gemini.ts`:
```typescript
const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "https://your-backend-url.com";
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
- The integrated mode (single service) is recommended for simplicity

