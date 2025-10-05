#!/bin/bash

# ForgetMeNot API Test Server Startup Script

echo "=========================================="
echo "ForgetMeNot API Server (TEST MODE)"
echo "=========================================="
echo ""
echo "⚠️  TEST MODE - Returns mock data"
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate venv
source venv/bin/activate

echo "🧪 Starting test server on http://localhost:8001"
echo "📚 API docs: http://localhost:8001/docs"
echo ""
echo "This server:"
echo "  ✅ Validates input data structure"
echo "  ✅ Returns mock/test data"
echo "  ❌ Does NOT actually process faces"
echo "  ❌ Does NOT call AI APIs"
echo ""

python test_main.py
