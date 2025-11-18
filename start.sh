#!/bin/bash

echo "🚀 Starting Profanity Filter Web Application..."
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "⚠️  Virtual environment not found."
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install/upgrade dependencies
echo "Checking dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "🌐 Starting Flask server..."
echo "📍 Application will be available at: http://localhost:8080"
echo "⌨️  Press Ctrl+C to stop the server"
echo ""

# Run the Flask app
python app.py
