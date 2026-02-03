#!/bin/bash
# Quick Run Script for AI Construction Assistant

echo "🏗️  AI Construction Assistant"
echo "===================================="
echo ""

cd "$(dirname "$0")"

# Activate virtual environment
source venv/bin/activate

# Run the application
PYTHONPATH=$(pwd) python backend/app.py
