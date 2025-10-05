#!/bin/bash

# ForgetMeNot API Server Startup Script

echo "=========================================="
echo "ForgetMeNot API Server"
echo "=========================================="
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate venv
source venv/bin/activate

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "Create .env with: GEMINI_API_KEY=your_api_key_here"
    echo ""
fi

# Start server
echo "🚀 Starting server on http://localhost:8000"
echo "📚 API docs: http://localhost:8000/docs"
echo ""

uvicorn main:app --host 0.0.0.0 --port 8000 --reload
