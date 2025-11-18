#!/bin/bash

# KIT CampusAI - Local Development Server
# This script runs the FastAPI backend locally for testing

set -e

echo "🚀 Starting KIT CampusAI Backend (Local Development Mode)"
echo "============================================================"

# Change to backend directory
cd "$(dirname "$0")"

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found!"
    echo "Please copy .env.example to .env and configure your API keys"
    exit 1
fi

echo "✅ Environment file found"

# Install/upgrade dependencies
echo "📚 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo "✅ Dependencies installed"

# Start uvicorn server
echo ""
echo "🌟 Starting FastAPI server..."
echo "============================================================"
echo "📍 API will be available at: http://localhost:8000"
echo "📖 API docs will be available at: http://localhost:8000/docs"
echo "🔍 Health check: http://localhost:8000/health"
echo "============================================================"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run uvicorn with hot reload
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
