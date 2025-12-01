# Two-Microservice Backend Setup

## Architecture

1. **Rewriter Service** (`rewriter-service/`) - Port 8001
   - Uses OpenAI to rewrite resumes into HTML
   - Endpoint: `POST /generate`

2. **PDF Service** (`pdf-service/`) - Port 8002
   - Converts HTML to PDF using WeasyPrint
   - Endpoint: `POST /generate`

3. **Gateway** (`main.py`) - Port 8000
   - Orchestrates calls to both microservices
   - Endpoints: `POST /upload`, `GET /result/{session_id}`

## Setup

### 1. Install dependencies for each service:

```bash
# Rewriter service
cd rewriter-service
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# PDF service
cd ../pdf-service
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Gateway (uses existing .venv)
cd ..
source .venv/bin/activate
```

### 2. Set environment variables:

```bash
export OPENAI_API_KEY="your-key-here"
```

### 3. Start all services:

**Terminal 1 - Rewriter Service:**
```bash
cd rewriter-service
source .venv/bin/activate
uvicorn main:app --port 8001 --reload
```

**Terminal 2 - PDF Service:**
```bash
cd pdf-service
source .venv/bin/activate
uvicorn main:app --port 8002 --reload
```

**Terminal 3 - Gateway:**
```bash
source .venv/bin/activate
uvicorn main:app --port 8000 --reload
```

**Terminal 4 - Frontend:**
```bash
npm run dev
```

## Testing

- Gateway: http://127.0.0.1:8000/docs
- Rewriter: http://127.0.0.1:8001/docs
- PDF Service: http://127.0.0.1:8002/docs

