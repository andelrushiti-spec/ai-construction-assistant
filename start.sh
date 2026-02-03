#!/bin/bash
# AI Construction Assistant - Quick Start Script

echo "🏗️  AI Construction Contract & Law Assistant"
echo "==========================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

# Check for .env file
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  WARNING: .env file not found!"
    echo "Please copy .env.example to .env and configure:"
    echo "  cp .env.example .env"
    echo "  nano .env  # Add your OPENAI_API_KEY"
    echo ""
    read -p "Press Enter to continue anyway or Ctrl+C to exit..."
fi

# Create necessary directories
mkdir -p logs uploads vector_db_storage

# Start the application
echo ""
echo "Starting AI Construction Assistant..."
echo "Access the application at: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

cd backend
python app.py
