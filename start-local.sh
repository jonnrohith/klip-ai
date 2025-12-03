#!/bin/bash

# Local Development Startup Script

echo "🚀 Starting Resumate AI Local Development..."
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3.11 -m venv .venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Check if dependencies are installed
if [ ! -f ".venv/bin/uvicorn" ]; then
    echo "📥 Installing Python dependencies..."
    pip install -r requirements.txt
fi

# Check if OPENAI_API_KEY is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  WARNING: OPENAI_API_KEY not set!"
    echo "   Set it with: export OPENAI_API_KEY='your-key-here'"
    echo ""
fi

# Start backend
echo "🔴 Starting backend server on http://127.0.0.1:8000"
echo "   API docs: http://127.0.0.1:8000/docs"
echo ""
uvicorn main:app --port 8000 --reload

